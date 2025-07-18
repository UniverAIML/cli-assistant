"""Chat Assistant module using transformer model for natural language processing."""

import json
import re
from typing import Dict, List, Any, Optional
from colorama import Fore, Style

from .function_definitions import FunctionDefinitions
from .function_executor import FunctionExecutor
from .operations_manager import OperationsManager
from .model_manager import ModelManager
from .config_manager import LoggerMixin


class ChatAssistant(LoggerMixin):
    """A chat assistant that uses transformer model for natural language processing."""

    def __init__(self) -> None:
        """Initialize the chat assistant with model and assistant stub."""

        # Initialize the model manager (Singleton)
        self.model_manager = ModelManager()

        # Initialize the operations manager
        self.operations = OperationsManager()

        # Initialize the function executor
        self.function_executor = FunctionExecutor(self.operations)

        self.conversation_history: List[Dict[str, str]] = []
        self.is_running = True

        # Get system prompt and function definitions from the dedicated class
        self.system_prompt = FunctionDefinitions.SYSTEM_PROMPT
        self.available_functions = FunctionDefinitions.AVAILABLE_FUNCTIONS

    def welcome_message(self) -> str:
        """Return a welcome message for the chat assistant."""
        return "🤖 Welcome to CLI Assistant with AI!"

    def parse_function_call(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse function call from model response."""
        # print(f"🔍 Debug - Parsing response: {response[:200]}...")  # Debug line

        # Check for OpenAI function call format first
        if response.startswith("FUNCTION_CALL:"):
            try:
                parts = response.split(":", 2)  # Split into max 3 parts
                if len(parts) >= 3:
                    function_name = parts[1]
                    arguments_json = parts[2]
                    arguments = json.loads(arguments_json)

                    function_call = {
                        "function": function_name,
                        "arguments": arguments,
                        "tool_call_id": f"call_{function_name}_{hash(arguments_json) % 10000}",
                    }
                    print(f"🔍 Debug - Found OpenAI function call: {function_call}")
                    return function_call
            except (json.JSONDecodeError, IndexError) as e:
                print(f"🔍 Debug - Error parsing OpenAI function call: {e}")

        # Look for JSON function call format in code blocks
        json_pattern = r"```json\s*(\{.*?\})\s*```"
        json_match = re.search(json_pattern, response, re.DOTALL)

        if json_match:
            try:
                function_call = json.loads(json_match.group(1))
                # Add tool_call_id if not present
                if "tool_call_id" not in function_call:
                    function_call["tool_call_id"] = (
                        f"call_{function_call.get('function', 'unknown')}_{hash(json_match.group(1)) % 10000}"
                    )
                # print(f"🔍 Debug - Found JSON in code block: {function_call}")  # Debug line
                return function_call  # type: ignore[no-any-return]
            except json.JSONDecodeError as e:
                print(f"🔍 Debug - JSON decode error in code block: {e}")  # Debug line

        # Look for JSON without code blocks
        json_pattern = r'\{[^{}]*"function"[^{}]*\}'
        json_match = re.search(json_pattern, response, re.DOTALL)

        if json_match:
            try:
                function_call = json.loads(json_match.group(0))
                # Add tool_call_id if not present
                if "tool_call_id" not in function_call:
                    function_call["tool_call_id"] = (
                        f"call_{function_call.get('function', 'unknown')}_{hash(json_match.group(0)) % 10000}"
                    )
                # print(f"🔍 Debug - Found JSON without code block: {function_call}")  # Debug line
                return function_call  # type: ignore[no-any-return]
            except json.JSONDecodeError as e:
                print(
                    f"🔍 Debug - JSON decode error without code block: {e}"
                )  # Debug line

        # Look for any JSON-like structure
        json_pattern = r'\{.*?"function".*?\}'
        json_match = re.search(json_pattern, response, re.DOTALL)

        if json_match:
            try:
                # Try to clean up the JSON
                json_str = json_match.group(0)
                function_call = json.loads(json_str)
                # Add tool_call_id if not present
                if "tool_call_id" not in function_call:
                    function_call["tool_call_id"] = (
                        f"call_{function_call.get('function', 'unknown')}_{hash(json_str) % 10000}"
                    )
                print(
                    f"\033[90m🔍 Debug - Found JSON-like structure: {function_call}\033[0m"
                )  # Debug line
                return function_call  # type: ignore[no-any-return]
            except json.JSONDecodeError as e:
                print(
                    f"🔍 Debug - JSON decode error in JSON-like structure: {e}"
                )  # Debug line

        # Print debug message in gray color using ANSI escape codes
        print(
            f"\033[90m🔍 Debug - No function call found in response\033[0m"
        )  # Gray debug line
        return None

    def execute_function_call(
        self, function_call: Dict[str, Any], user_input: str
    ) -> str:
        """Execute the function call using the function executor."""
        return self.function_executor.execute_function_call(function_call, user_input)

    def generate_function_calling_response(self, user_input: str) -> str:
        """Generate response using function calling capabilities."""
        try:
            # Prepare messages using model manager
            messages = self.model_manager.prepare_messages(
                user_input, self.conversation_history
            )

            # Generate response using model manager
            assistant_response = self.model_manager.generate_function_calling_response(
                messages
            )

            # Try to parse function call
            function_call = self.parse_function_call(assistant_response)

            if function_call:
                # Execute function and get result
                function_result = self.execute_function_call(function_call, user_input)

                # Add the assistant's function call message to messages
                assistant_tool_message = {
                    "role": "assistant",
                    "content": assistant_response,
                    "tool_calls": [
                        {
                            "id": function_call.get(
                                "tool_call_id", f"call_{function_call['function']}"
                            ),
                            "type": "function",
                            "function": {
                                "name": function_call["function"],
                                "arguments": json.dumps(function_call["arguments"]),
                            },
                        }
                    ],
                }

                # Create a copy of messages to avoid modifying original
                messages_copy = messages.copy()
                messages_copy.append(assistant_tool_message)  # type: ignore

                # Add the function result as a tool message
                tool_message = {
                    "role": "tool",
                    "tool_call_id": function_call.get(
                        "tool_call_id", f"call_{function_call['function']}"
                    ),
                    "name": function_call["function"],
                    "content": function_result,
                }
                messages_copy.append(tool_message)  # type: ignore

                # Generate final response based on function result
                final_response = self.model_manager.generate_function_calling_response(
                    messages_copy
                )

                return final_response

            else:
                # If no function call, check for keyword-based commands (fallback)
                if "help" in user_input.lower() and (
                    "command" in assistant_response.lower()
                    or "help" in assistant_response.lower()
                ):
                    return FunctionDefinitions.HELP_MESSAGE

                # Return the assistant's natural language response
                return assistant_response

        except Exception as e:
            self.logger.error(f"Error in function calling response: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"

    def generate_response(self, user_input: str) -> str:
        """Generate a response based on user input using AI."""
        if not user_input.strip():
            return "I didn't catch that. Could you please say something?"

        # Check for exit commands
        if any(cmd in user_input.lower() for cmd in ["exit", "quit", "bye", "goodbye"]):
            self.is_running = False
            return "Goodbye! Have a great day!"

        # Let the function calling model handle everything
        response = self.generate_function_calling_response(user_input)

        return response

    def add_to_history(self, user_input: str, assistant_response: str) -> None:
        """Add conversation to history."""
        self.conversation_history.append(
            {"user": user_input, "assistant": assistant_response}
        )

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return self.conversation_history.copy()

    def chat_loop(self) -> None:
        """Main chat loop for interactive conversation."""
        print(self.welcome_message())
        print("\n" + "=" * 50 + "\n")

        while self.is_running:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                response = self.generate_response(user_input)
                print(f"\nAssistant: {response}\n")

                self.add_to_history(user_input, response)

                if not self.is_running:
                    break

            except KeyboardInterrupt:
                print("\n\nGoodbye! Thanks for chatting!")
                break
            except Exception as e:
                print(f"\nSorry, I encountered an error: {e}")
                print("Let's try again!\n")
