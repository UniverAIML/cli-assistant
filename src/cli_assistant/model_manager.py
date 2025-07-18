"""Model management and response generation strategies."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from .config_manager import ConfigurationManager, LoggerMixin
from .function_definitions import FunctionDefinitions


class ResponseStrategy(ABC):
    """Abstract strategy for generating responses."""

    @abstractmethod
    def generate_response(
        self, 
        model: Any, 
        tokenizer: Any, 
        messages: List[Dict[str, str]], 
        **kwargs: Any
    ) -> str:
        """Generate a response using the specific strategy."""
        pass


class FunctionCallingStrategy(ResponseStrategy):
    """Strategy for generating function calling responses."""

    def generate_response(
        self, 
        model: Any, 
        tokenizer: Any, 
        messages: List[Dict[str, str]], 
        **kwargs: Any
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
        response: str = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response


class ContextualResponseStrategy(ResponseStrategy):
    """Strategy for generating contextual follow-up responses."""

    def generate_response(
        self, 
        model: Any, 
        tokenizer: Any, 
        messages: List[Dict[str, str]], 
        **kwargs: Any
    ) -> str:
        """Generate a contextual response based on function execution result."""
        # Format prompt using chat template
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        # Use different generation parameters for contextual responses
        contextual_kwargs = {
            "max_new_tokens": 150,
            "temperature": 0.5,
            "do_sample": True,
            "pad_token_id": tokenizer.eos_token_id,
        }

        # Generate contextual response using direct model call
        generated_ids = model.generate(**model_inputs, **contextual_kwargs)

        # Extract only the new tokens
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        # Extract response
        response: str = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response.strip()


class ModelManager(LoggerMixin):
    """
    Manages AI model loading and inference using Strategy pattern.
    Implements Singleton pattern for model instance management.
    """

    _instance = None
    _model_loaded = False

    def __new__(cls) -> 'ModelManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._model_loaded:
            self.config_manager = ConfigurationManager()
            self._load_model()
            self._setup_strategies()
            ModelManager._model_loaded = True

    def _load_model(self) -> None:
        """Load the AI model and tokenizer."""
        try:
            model_config = self.config_manager.model_config
            system_config = self.config_manager.system_config

            self.logger.info(f"Loading model: {model_config.model_name}")

            # Get model loading arguments
            model_kwargs = self.config_manager.get_model_kwargs()

            self.model = AutoModelForCausalLM.from_pretrained(
                model_config.model_name, **model_kwargs
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_config.model_name)

            # Move model to appropriate device if not using accelerate
            if not system_config.use_accelerate and system_config.device_type != "cpu":
                self.model = self.model.to(system_config.device_type)

            self.logger.info("Model loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            raise RuntimeError(f"Failed to load model: {str(e)}")

    def _setup_strategies(self) -> None:
        """Setup response generation strategies."""
        self.function_calling_strategy = FunctionCallingStrategy()
        self.contextual_strategy = ContextualResponseStrategy()

    def generate_function_calling_response(self, messages: List[Dict[str, str]]) -> str:
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

    def generate_contextual_response(
        self, user_input: str, function_call: Dict[str, Any], function_result: str
    ) -> str:
        """Generate contextual response based on function execution result."""
        try:
            # Create a follow-up prompt with the function result
            context_messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Based on the user's request and the function execution result, provide a natural, conversational response. Be friendly and informative.",
                },
                {"role": "user", "content": f"User asked: '{user_input}'"},
                {
                    "role": "assistant",
                    "content": f"I executed the function '{function_call.get('function')}' and got this result: {function_result}",
                },
                {
                    "role": "user",
                    "content": "Now respond naturally to the user based on what happened.",
                },
            ]

            contextual_response = self.contextual_strategy.generate_response(
                self.model, self.tokenizer, context_messages
            )

            # Clean up the response and ensure it's natural
            if contextual_response:
                # If the response is too short or seems incomplete, fallback to function result
                if (
                    len(contextual_response) < 10
                    or "function" in contextual_response.lower()
                ):
                    return function_result

                return contextual_response
            else:
                return function_result

        except Exception as e:
            # Fallback to function result if anything goes wrong
            self.logger.error(f"Error in contextual response: {str(e)}")
            return function_result

    def prepare_messages(
        self, user_input: str, conversation_history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
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

        return messages
