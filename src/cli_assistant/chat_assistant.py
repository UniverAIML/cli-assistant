"""Chat Assistant module using transformer model for natural language processing."""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, List, Any, Optional
import json
import re
import platform
import sys
import logging
import os

# Disable transformers warnings and progress bars
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("accelerate").setLevel(logging.ERROR)
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Disable tqdm progress bars globally
try:
    from tqdm import tqdm
    tqdm.disable = True
except ImportError:
    pass

from .assistant_stub import AssistantStub
from .function_definitions import FunctionDefinitions


class ChatAssistant:
    """A chat assistant that uses transformer model for natural language processing."""

    def __init__(self) -> None:
        """Initialize the chat assistant with model and assistant stub."""

        try:
            # Detect platform and available acceleration
            system_platform = platform.system().lower()
            cuda_available = torch.cuda.is_available()
            mps_available = (
                torch.backends.mps.is_available()
                if hasattr(torch.backends, "mps")
                else False
            )

            # Determine optimal device configuration
            if system_platform == "darwin" and mps_available:
                # macOS with Apple Silicon
                device_type = "mps"
                torch_dtype = torch.float16
                device_map = None
                use_accelerate = False
                device_info = f"Platform: macOS, MPS available: {mps_available}"
            elif cuda_available and system_platform in ["windows", "linux"]:
                # Windows/Linux with NVIDIA GPU
                device_type = "cuda"
                torch_dtype = torch.float16
                device_map = "auto"
                use_accelerate = True
                device_info = f"Platform: {system_platform}, CUDA available: {cuda_available}, GPU count: {torch.cuda.device_count()}, Current device: {torch.cuda.get_device_name()}"
            else:
                # CPU fallback for any platform
                device_type = "cpu"
                torch_dtype = torch.float32
                device_map = None
                use_accelerate = False
                device_info = f"Platform: {system_platform}, Using CPU mode"

            # Load model with appropriate configuration (following official Qwen example)
            model_name = "Qwen/Qwen2.5-Coder-3B-Instruct"
            
            # Use official Qwen configuration approach
            model_kwargs = {
                "torch_dtype": "auto",  # Let model decide optimal dtype
                "trust_remote_code": True
            }
            
            if use_accelerate:
                model_kwargs["device_map"] = "auto"  # Let accelerate decide optimal mapping
            
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name, **model_kwargs
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)

            # Move model to appropriate device if not using accelerate
            if not use_accelerate and device_type != "cpu":
                self.model = self.model.to(device_type)

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")

        # Initialize the assistant stub for handling commands
        self.assistant = AssistantStub()

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
        #print(f"🔍 Debug - Parsing response: {response[:200]}...")  # Debug line
        
        # Look for JSON function call format in code blocks
        json_pattern = r"```json\s*(\{.*?\})\s*```"
        json_match = re.search(json_pattern, response, re.DOTALL)

        if json_match:
            try:
                function_call = json.loads(json_match.group(1))
                print(f"🔍 Debug - Found JSON in code block: {function_call}")  # Debug line
                return function_call  # type: ignore[no-any-return]
            except json.JSONDecodeError as e:
                print(f"🔍 Debug - JSON decode error in code block: {e}")  # Debug line

        # Look for JSON without code blocks
        json_pattern = r'\{[^{}]*"function"[^{}]*\}'
        json_match = re.search(json_pattern, response, re.DOTALL)

        if json_match:
            try:
                function_call = json.loads(json_match.group(0))
                print(f"🔍 Debug - Found JSON without code block: {function_call}")  # Debug line
                return function_call  # type: ignore[no-any-return]
            except json.JSONDecodeError as e:
                print(f"🔍 Debug - JSON decode error without code block: {e}")  # Debug line

        # Look for any JSON-like structure
        json_pattern = r'\{.*?"function".*?\}'
        json_match = re.search(json_pattern, response, re.DOTALL)

        if json_match:
            try:
                # Try to clean up the JSON
                json_str = json_match.group(0)
                function_call = json.loads(json_str)
                print(f"🔍 Debug - Found JSON-like structure: {function_call}")  # Debug line
                return function_call  # type: ignore[no-any-return]
            except json.JSONDecodeError as e:
                print(f"🔍 Debug - JSON decode error in JSON-like structure: {e}")  # Debug line

        print(f"🔍 Debug - No function call found in response")  # Debug line
        return None

    def execute_function_call(
        self, function_call: Dict[str, Any], user_input: str
    ) -> str:
        """Execute the function call and return appropriate response."""
        function_name = function_call.get("function")
        arguments = function_call.get("arguments", {})

        print(f"🔧 Executing: {function_name}({arguments})")

        try:
            if function_name == "add_contact":
                name = arguments.get("name", "")
                phones = arguments.get("phones", [])
                birthday = arguments.get("birthday", "")

                # Execute the function and get result
                self.assistant.add_contact()
                result = True  # Assume success for stub

                # Format response based on execution result
                if result:
                    return f"✅ Successfully added contact: {name}" + (
                        f" with {len(phones)} phone(s)" if phones else ""
                    )
                else:
                    return "❌ Failed to add contact. Please try again."

            elif function_name == "search_contacts":
                query = arguments.get("query", user_input)
                contacts = self.assistant.search_contacts(query)

                if contacts and len(contacts) > 0:
                    return f"📞 Found {len(contacts)} contact(s) matching '{query}'"
                else:
                    return f"❌ No contacts found matching '{query}'"

            elif function_name == "show_contacts":
                self.assistant.display_contacts_table()
                contacts = []  # Assume empty result for stub

                if contacts:
                    return f"📞 Here are all your contacts ({len(contacts)} total)"
                else:
                    return "📞 No contacts found. Add some contacts first!"

            elif function_name == "edit_contact":
                name = arguments.get("name", "")
                action = arguments.get("action", "")
                
                self.assistant.edit_contact()
                success = True  # Assume success for stub
                
                if success:
                    return f"✅ Successfully edited contact: {name} (action: {action})"
                else:
                    return f"❌ Failed to edit contact: {name}"

            elif function_name == "delete_contact":
                name = arguments.get("name", "")
                
                self.assistant.delete_contact()
                success = True  # Assume success for stub
                
                if success:
                    return f"✅ Successfully deleted contact: {name}"
                else:
                    return f"❌ Failed to delete contact: {name}"

            elif function_name == "view_contact_details":
                name = arguments.get("name", "")
                
                self.assistant.view_contact_details()
                success = True  # Assume success for stub
                
                if success:
                    return f"📞 Showing details for contact: {name}"
                else:
                    return f"❌ Contact not found: {name}"

            elif function_name == "add_note":
                title = arguments.get("title", "")
                content = arguments.get("content", "")
                tags = arguments.get("tags", [])

                self.assistant.add_note()
                success = True  # Assume success for stub

                if success:
                    return f"📝 Successfully added note: '{title}'" + (
                        f" with {len(tags)} tag(s)" if tags else ""
                    )
                else:
                    return "❌ Failed to add note. Please try again."

            elif function_name == "search_notes":
                query = arguments.get("query", user_input)
                notes_result = self.assistant.search_notes(query)

                if notes_result and len(notes_result) > 0:
                    return f"📝 Found {len(notes_result)} note(s) matching '{query}'"
                else:
                    return f"❌ No notes found matching '{query}'"

            elif function_name == "show_notes":
                self.assistant.display_notes_table()
                notes: List[Any] = []  # Assume empty result for stub

                if notes:
                    return f"📝 Here are all your notes ({len(notes)} total)"
                else:
                    return "📝 No notes found. Create some notes first!"

            elif function_name == "edit_note":
                note_id = arguments.get("note_id", "")
                action = arguments.get("action", "")
                
                self.assistant.edit_note()
                success = True  # Assume success for stub
                
                if success:
                    return f"✅ Successfully edited note: {note_id} (action: {action})"
                else:
                    return f"❌ Failed to edit note: {note_id}"

            elif function_name == "delete_note":
                note_id = arguments.get("note_id", "")
                
                self.assistant.delete_note()
                success = True  # Assume success for stub
                
                if success:
                    return f"✅ Successfully deleted note: {note_id}"
                else:
                    return f"❌ Failed to delete note: {note_id}"

            elif function_name == "view_note_details":
                note_id = arguments.get("note_id", "")
                
                self.assistant.view_note_details()
                success = True  # Assume success for stub
                
                if success:
                    return f"📝 Showing details for note: {note_id}"
                else:
                    return f"❌ Note not found: {note_id}"

            elif function_name == "search_notes_by_tag":
                tag = arguments.get("tag", "")
                
                notes_result = self.assistant.search_notes(tag)  # Using existing method
                
                if notes_result and len(notes_result) > 0:
                    return f"📝 Found {len(notes_result)} note(s) with tag '{tag}'"
                else:
                    return f"❌ No notes found with tag '{tag}'"

            elif function_name == "global_search":
                query = arguments.get("query", user_input)
                
                contacts = self.assistant.search_contacts(query)
                notes_result = self.assistant.search_notes(query)
                
                contact_count = len(contacts) if contacts else 0
                note_count = len(notes_result) if notes_result else 0
                total_results = contact_count + note_count
                
                if total_results > 0:
                    return f"🔍 Global search found {total_results} result(s): {contact_count} contact(s) and {note_count} note(s) matching '{query}'"
                else:
                    return f"❌ No results found for '{query}'"

            elif function_name == "get_statistics":
                stats = self.assistant.get_statistics()

                if stats:
                    return f"📊 Statistics: {stats}"
                else:
                    return "📊 No statistics available yet."

            elif function_name == "get_upcoming_birthdays":
                days = arguments.get("days", 7)
                birthdays = self.assistant.get_upcoming_birthdays(days)

                if birthdays and len(birthdays) > 0:
                    return f"🎂 Found {len(birthdays)} upcoming birthday(s) in the next {days} days"
                else:
                    return f"🎂 No upcoming birthdays in the next {days} days"

            elif function_name == "show_help":
                return FunctionDefinitions.HELP_MESSAGE

            else:
                return f"❌ Unknown function: {function_name}"

        except Exception as e:
            return f"❌ Error executing {function_name}: {str(e)}"

    def generate_function_calling_response(self, user_input: str) -> str:
        """Generate response using function calling capabilities."""
        try:
            # Prepare the prompt with available functions and conversation history
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt,
                }
            ]

            # Add recent conversation history (last 5 exchanges to avoid context overflow)
            recent_history = (
                self.conversation_history[-5:]
                if len(self.conversation_history) > 5
                else self.conversation_history
            )
            for exchange in recent_history:
                messages.append({"role": "user", "content": exchange["user"]})
                messages.append({"role": "assistant", "content": exchange["assistant"]})

            # Add current user input
            messages.append({"role": "user", "content": user_input})

            # Generate response using direct model call (following official Qwen example)
            text = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=300,  # Increased for function calls
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
            
            # Extract only the new tokens (remove input)
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]

            # Decode the response
            assistant_response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            #print(f"🔍 Debug - Assistant response: {assistant_response}")  # Debug line

            # Try to parse function call
            function_call = self.parse_function_call(assistant_response)
            #print(f"🔍 Debug - Parsed function call: {function_call}")  # Debug line

            if function_call:
                # Execute function and get result
                function_result = self.execute_function_call(function_call, user_input)

                # Generate a more natural response based on the function result
                return self.generate_contextual_response(
                    user_input, function_call, function_result
                )
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
            print(f"🔍 Debug - Error: {str(e)}")  # Debug line
            return f"Sorry, I encountered an error: {str(e)}"

    def generate_contextual_response(
        self, user_input: str, function_call: Dict[str, Any], function_result: str
    ) -> str:
        """Generate a contextual response based on the function execution result."""
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

            # Format prompt using chat template
            text = self.tokenizer.apply_chat_template(
                context_messages, tokenize=False, add_generation_prompt=True
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

            # Generate contextual response using direct model call
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=150,
                temperature=0.5,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
            
            # Extract only the new tokens
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]

            # Extract response
            contextual_response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

            # Clean up the response and ensure it's natural
            if contextual_response:
                # Remove any function call references or technical details
                contextual_response = contextual_response.strip()

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
            print(f"🔍 Debug - Error in contextual response: {str(e)}")
            return function_result

    def generate_response(self, user_input: str) -> str:
        """Generate a response based on user input using AI."""
        if not user_input.strip():
            return "I didn't catch that. Could you please say something?"

        # Check for exit commands
        if any(cmd in user_input.lower() for cmd in ["exit", "quit", "bye", "goodbye"]):
            self.is_running = False
            return "Goodbye! Have a great day!"

        # Let the function calling model handle everything
        return self.generate_function_calling_response(user_input)

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
