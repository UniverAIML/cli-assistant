"""Model management and response generation strategies."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, cast, Literal
from typing_extensions import TypedDict
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import json
import openai
from openai.types.chat import ChatCompletionMessageParam

from .config_manager import ConfigurationManager, LoggerMixin
from .function_definitions import FunctionDefinitions


# Define TypedDict classes for message parameters
class SystemMessage(TypedDict):
    role: Literal["system"]
    content: str


class UserMessage(TypedDict):
    role: Literal["user"]
    content: str


class AssistantMessage(TypedDict):
    role: Literal["assistant"]
    content: Optional[str]


class AssistantToolCallMessage(TypedDict):
    role: Literal["assistant"]
    content: Optional[str]
    tool_calls: List[Dict[str, Any]]


class ToolMessage(TypedDict):
    role: Literal["tool"]
    tool_call_id: str
    name: str
    content: str


# Union type for all possible message types
MessageType = Union[
    SystemMessage, UserMessage, AssistantMessage, AssistantToolCallMessage, ToolMessage
]


class ResponseStrategy(ABC):
    """Abstract strategy for generating responses."""

    @abstractmethod
    def generate_response(
        self, model: Any, tokenizer: Any, messages: List[Dict[str, Any]], **kwargs: Any
    ) -> str:
        """Generate a response using the specific strategy."""
        pass


class FunctionCallingStrategy(ResponseStrategy):
    """Strategy for generating function calling responses."""

    def generate_response(
        self, model: Any, tokenizer: Any, messages: List[Dict[str, Any]], **kwargs: Any
    ) -> str:
        """Generate response with function calling capabilities."""
        # Generate response using direct model call (following official Qwen example)
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        generation_kwargs = kwargs.get("generation_kwargs", {})
        generation_kwargs.setdefault("pad_token_id", tokenizer.eos_token_id)

        generated_ids = model.generate(**model_inputs, **generation_kwargs)

        # Extract only the new tokens (remove input)
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        # Decode the response
        response: str = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[
            0
        ]
        return response


class OpenAIStrategy(ResponseStrategy):
    """Strategy for generating responses using OpenAI API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        # Use API key from parameter, environment variable, or default
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        self.model_name = model
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_response(
        self,
        model: Any,  # Not used for OpenAI, but kept for interface compatibility
        tokenizer: Any,  # Not used for OpenAI, but kept for interface compatibility
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """Generate response using OpenAI API."""
        try:
            if not self.client:
                raise RuntimeError("OpenAI client not initialized")

            # Import function definitions
            from .function_definitions import FunctionDefinitions

            # Convert function definitions to OpenAI tools format
            tools = []
            for func_name, func_def in FunctionDefinitions.AVAILABLE_FUNCTIONS.items():
                tool = {
                    "type": "function",
                    "function": {
                        "name": func_def["name"],
                        "description": func_def["description"],
                        "parameters": func_def["parameters"],
                    },
                }
                tools.append(tool)

            # Create completion with function calling support
            # Convert messages to proper OpenAI format
            openai_messages: List[ChatCompletionMessageParam] = []
            for msg in messages:
                if msg["role"] == "system":
                    openai_messages.append(
                        cast(
                            ChatCompletionMessageParam,
                            {"role": "system", "content": msg["content"]},
                        )
                    )
                elif msg["role"] == "user":
                    openai_messages.append(
                        cast(
                            ChatCompletionMessageParam,
                            {"role": "user", "content": msg["content"]},
                        )
                    )
                elif msg["role"] == "assistant":
                    if "tool_calls" in msg:
                        # Assistant message with tool calls
                        openai_messages.append(
                            cast(
                                ChatCompletionMessageParam,
                                {
                                    "role": "assistant",
                                    "content": msg.get("content"),
                                    "tool_calls": msg["tool_calls"],
                                },
                            )
                        )
                    else:
                        # Regular assistant message
                        openai_messages.append(
                            cast(
                                ChatCompletionMessageParam,
                                {"role": "assistant", "content": msg["content"]},
                            )
                        )
                elif msg["role"] == "tool":
                    # Tool message with result
                    openai_messages.append(
                        cast(
                            ChatCompletionMessageParam,
                            {
                                "role": "tool",
                                "tool_call_id": msg["tool_call_id"],
                                "name": msg["name"],
                                "content": msg["content"],
                            },
                        )
                    )

            # Create the API call with proper parameters
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,  # type: ignore
                tools=tools,  # type: ignore
                tool_choice="auto",
                max_tokens=kwargs.get("max_tokens"),
                temperature=kwargs.get("temperature"),
                top_p=kwargs.get("top_p"),
            )

            message = response.choices[0].message

            # Check if OpenAI wants to call a function
            if message.tool_calls:
                # Return the function call information in a format our system expects
                tool_call = message.tool_calls[0]
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    function_args = {}

                # Format as expected by our function executor
                result = f"FUNCTION_CALL:{function_name}:{json.dumps(function_args)}"
                return result
            else:
                # Regular text response
                return message.content.strip() if message.content else ""

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")


class ModelManager(LoggerMixin):
    """
    Manages AI model loading and inference using Strategy pattern.
    Implements Singleton pattern for model instance management.
    """

    _instance = None
    _model_loaded = False

    def __new__(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._model_loaded:
            self.config_manager = ConfigurationManager()
            self.function_calling_strategy: ResponseStrategy
            self.model: Optional[Any] = None
            self.tokenizer: Optional[Any] = None
            self.use_openai: bool = False

            # Check if we should use OpenAI or local model
            use_openai = os.getenv("USE_OPENAI", "false").lower() == "true"

            if use_openai:
                self._setup_openai()
            else:
                self._load_model()

            self._setup_strategies()
            ModelManager._model_loaded = True

    def _setup_openai(self) -> None:
        """Setup OpenAI API instead of loading local model."""
        try:
            openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

            # Create dummy model and tokenizer attributes for compatibility
            self.model = None
            self.tokenizer = None
            self.use_openai = True

        except Exception as e:
            self.logger.error(f"Failed to setup OpenAI: {str(e)}")
            raise RuntimeError(f"Failed to setup OpenAI: {str(e)}")

    def _load_model(self) -> None:
        """Load the AI model and tokenizer."""
        try:
            model_config = self.config_manager.model_config
            system_config = self.config_manager.system_config

            # Get model loading arguments
            model_kwargs = self.config_manager.get_model_kwargs()

            self.model = AutoModelForCausalLM.from_pretrained(
                model_config.model_name, **model_kwargs
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_config.model_name)

            # Move model to appropriate device if not using accelerate
            if (
                not system_config.use_accelerate
                and system_config.device_type != "cpu"
                and self.model is not None
            ):
                self.model = self.model.to(system_config.device_type)

        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            raise RuntimeError(f"Failed to load model: {str(e)}")

    def _setup_strategies(self) -> None:
        """Setup response generation strategies."""
        if hasattr(self, "use_openai") and self.use_openai:
            # Setup OpenAI strategies
            openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
            self.function_calling_strategy = OpenAIStrategy(model=openai_model)
        else:
            # Setup local model strategies
            self.function_calling_strategy = FunctionCallingStrategy()

    def generate_function_calling_response(self, messages: List[Dict[str, Any]]) -> str:
        """Generate response using function calling strategy."""
        try:
            generation_kwargs = self.config_manager.get_generation_kwargs()
            return self.function_calling_strategy.generate_response(
                self.model,
                self.tokenizer,
                messages,
                generation_kwargs=generation_kwargs,
            )
        except Exception as e:
            self.logger.error(f"Error in function calling response: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"

    def prepare_messages(
        self, user_input: str, conversation_history: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Prepare messages for model input."""
        messages = [
            {
                "role": "system",
                "content": FunctionDefinitions.SYSTEM_PROMPT,
            }
        ]

        # Add recent conversation history (last 5 exchanges to avoid context overflow)
        recent_history = (
            conversation_history[-5:]
            if len(conversation_history) > 5
            else conversation_history
        )
        for exchange in recent_history:
            messages.append({"role": "user", "content": exchange["user"]})
            messages.append({"role": "assistant", "content": exchange["assistant"]})

        # Add current user input
        messages.append({"role": "user", "content": user_input})

        return messages  # type: ignore
