"""Chat Assistant module using Qwen2 transformer model for natural language processing."""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.pipelines import pipeline
from typing import Dict, List, Any, Optional
import json
import re

from .assistant_stub import AssistantStub
from .function_definitions import FunctionDefinitions


class ChatAssistant:
    """A chat assistant that uses Qwen2-1.5B-Instruct-Function-Calling transformer model for natural language processing."""
    
    def __init__(self) -> None:
        """Initialize the chat assistant with Qwen2 Function-Calling model and assistant stub."""
        print("🔄 Loading AI model...")
        
        try:
            # Check CUDA availability
            cuda_available = torch.cuda.is_available()
            device_info = f"CUDA available: {cuda_available}"
            if cuda_available:
                device_info += f", GPU count: {torch.cuda.device_count()}, Current device: {torch.cuda.get_device_name()}"
            print(f"🔍 Device info: {device_info}")
            
            # Load Qwen2-1.5B Function-Calling model and tokenizer
            model_name = "devanshamin/Qwen2-1.5B-Instruct-Function-Calling-v1"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if cuda_available else torch.float32,
                device_map="auto" if cuda_available else None,
                trust_remote_code=True
            )
            
            # Create text generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=2024,
                temperature=0.1,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                device=0 if cuda_available else -1  # Explicitly set device
            )
            
            print(f"✅ Model loaded successfully on {'GPU' if cuda_available else 'CPU'}!")
            
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
        return (
            "🤖 Welcome to CLI Assistant with AI!"
        )
    
    def extract_assistant_response(self, generated_text: str, prompt: str) -> str:
        """Extract the assistant's response from the generated text."""
        # Remove the original prompt from the generated text
        if prompt in generated_text:
            response = generated_text.replace(prompt, "").strip()
        else:
            # Fallback: look for assistant markers
            if "<|im_start|>assistant" in generated_text:
                response = generated_text.split("<|im_start|>assistant")[-1]
                if "<|im_end|>" in response:
                    response = response.split("<|im_end|>")[0]
                response = response.strip()
            else:
                response = generated_text.strip()
        
        return response
    
    def parse_function_call(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse function call from model response."""
        # Look for JSON function call format
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        json_match = re.search(json_pattern, response, re.DOTALL)
        
        if json_match:
            try:
                function_call = json.loads(json_match.group(1))
                return function_call
            except json.JSONDecodeError:
                pass
        
        # Look for direct JSON without code blocks
        json_pattern = r'\{[^}]*"function"[^}]*\}'
        json_match = re.search(json_pattern, response, re.DOTALL)
        
        if json_match:
            try:
                function_call = json.loads(json_match.group(0))
                return function_call
            except json.JSONDecodeError:
                pass
        
        return None
    
    def execute_function_call(self, function_call: Dict[str, Any], user_input: str) -> str:
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
                result = self.assistant.add_contact()
                
                # Format response based on execution result
                if result:
                    return f"✅ Successfully added contact: {name}" + (f" with {len(phones)} phone(s)" if phones else "")
                else:
                    return "❌ Failed to add contact. Please try again."
            
            elif function_name == "search_contacts":
                query = arguments.get("query", user_input)
                result = self.assistant.search_contacts(query)
                
                if result and len(result) > 0:
                    return f"📞 Found {len(result)} contact(s) matching '{query}'"
                else:
                    return f"❌ No contacts found matching '{query}'"
            
            elif function_name == "show_contacts":
                result = self.assistant.display_contacts_table()
                
                if result:
                    return f"📞 Here are all your contacts ({len(result)} total)"
                else:
                    return "📞 No contacts found. Add some contacts first!"
            
            elif function_name == "add_note":
                title = arguments.get("title", "")
                content = arguments.get("content", "")
                tags = arguments.get("tags", [])
                
                result = self.assistant.add_note()
                
                if result:
                    return f"📝 Successfully added note: '{title}'" + (f" with {len(tags)} tag(s)" if tags else "")
                else:
                    return "❌ Failed to add note. Please try again."
                    
            elif function_name == "search_notes":
                query = arguments.get("query", user_input)
                result = self.assistant.search_notes(query)
                
                if result and len(result) > 0:
                    return f"📝 Found {len(result)} note(s) matching '{query}'"
                else:
                    return f"❌ No notes found matching '{query}'"
            
            elif function_name == "show_notes":
                result = self.assistant.display_notes_table()
                
                if result:
                    return f"📝 Here are all your notes ({len(result)} total)"
                else:
                    return "📝 No notes found. Create some notes first!"
            
            elif function_name == "get_statistics":
                stats = self.assistant.get_statistics()
                
                if stats:
                    return f"📊 Statistics: {stats}"
                else:
                    return "📊 No statistics available yet."
            
            elif function_name == "get_upcoming_birthdays":
                days = arguments.get("days", 7)
                result = self.assistant.get_upcoming_birthdays(days)
                
                if result and len(result) > 0:
                    return f"🎂 Found {len(result)} upcoming birthday(s) in the next {days} days"
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
                    "content": f"{self.system_prompt}\n\nAvailable functions with descriptions: {json.dumps(self.available_functions, indent=2)}"
                }
            ]
            
            # Add recent conversation history (last 5 exchanges to avoid context overflow)
            recent_history = self.conversation_history[-5:] if len(self.conversation_history) > 5 else self.conversation_history
            for exchange in recent_history:
                messages.append({"role": "user", "content": exchange["user"]})
                messages.append({"role": "assistant", "content": exchange["assistant"]})
            
            # Add current user input
            messages.append({
                "role": "user", 
                "content": user_input
            })
            
            # Format prompt for Qwen2 Function-Calling
            prompt = self.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # Generate response
            response = self.generator(
                prompt,
                max_new_tokens=300,
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract generated text
            generated_text = response[0]["generated_text"]
            # print(f"🔍 Debug - Generated text: {generated_text}")  # Debug line
            
            # Extract only the assistant's response
            assistant_response = self.extract_assistant_response(generated_text, prompt)
            # print(f"🔍 Debug - Assistant response: {assistant_response}")  # Debug line
            
            # Try to parse function call
            function_call = self.parse_function_call(assistant_response)
            
            if function_call:
                # Execute function and get result
                function_result = self.execute_function_call(function_call, user_input)
                
                # Generate a more natural response based on the function result
                return self.generate_contextual_response(user_input, function_call, function_result)
            else:
                # If no function call, check for keyword-based commands (fallback)
                if "help" in user_input.lower() and ("command" in assistant_response.lower() or "help" in assistant_response.lower()):
                    return FunctionDefinitions.HELP_MESSAGE
                
                # Return the assistant's natural language response
                return assistant_response
            
        except Exception as e:
            print(f"🔍 Debug - Error: {str(e)}")  # Debug line
            return f"Sorry, I encountered an error: {str(e)}"
    
    def generate_contextual_response(self, user_input: str, function_call: Dict[str, Any], function_result: str) -> str:
        """Generate a contextual response based on the function execution result."""
        try:
            # Create a follow-up prompt with the function result
            context_messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Based on the user's request and the function execution result, provide a natural, conversational response. Be friendly and informative."
                },
                {
                    "role": "user",
                    "content": f"User asked: '{user_input}'"
                },
                {
                    "role": "assistant", 
                    "content": f"I executed the function '{function_call.get('function')}' and got this result: {function_result}"
                },
                {
                    "role": "user",
                    "content": "Now respond naturally to the user based on what happened."
                }
            ]
            
            # Format prompt
            prompt = self.tokenizer.apply_chat_template(
                context_messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Generate contextual response
            response = self.generator(
                prompt,
                max_new_tokens=150,
                temperature=0.5,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract response
            generated_text = response[0]["generated_text"]
            contextual_response = self.extract_assistant_response(generated_text, prompt)
            
            # Clean up the response and ensure it's natural
            if contextual_response:
                # Remove any function call references or technical details
                contextual_response = contextual_response.strip()
                
                # If the response is too short or seems incomplete, fallback to function result
                if len(contextual_response) < 10 or "function" in contextual_response.lower():
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
        self.conversation_history.append({
            "user": user_input,
            "assistant": assistant_response
        })
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return self.conversation_history.copy()
    
    def chat_loop(self) -> None:
        """Main chat loop for interactive conversation."""
        print(self.welcome_message())
        print("\n" + "="*50 + "\n")
        
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