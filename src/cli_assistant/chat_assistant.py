"""Chat Assistant module using spaCy for natural language processing."""

import spacy
from typing import Dict, List, Optional, Any
import re


class ChatAssistant:
    """A chat assistant that uses spaCy for natural language processing."""
    
    def __init__(self) -> None:
        """Initialize the chat assistant with spaCy model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' not found. "
                "Please install it using: python -m spacy download en_core_web_sm"
            )
        
        self.conversation_history: List[Dict[str, str]] = []
        self.is_running = True
        
        # Define some simple response patterns
        self.response_patterns = {
            "greeting": {
                "patterns": ["hello", "hi", "hey", "greetings"],
                "responses": [
                    "Hello! How can I help you today?",
                    "Hi there! What would you like to know?",
                    "Greetings! I'm here to assist you."
                ]
            },
            "goodbye": {
                "patterns": ["bye", "goodbye", "exit", "quit", "see you"],
                "responses": [
                    "Goodbye! Have a great day!",
                    "See you later!",
                    "Take care!"
                ]
            },
            "help": {
                "patterns": ["help", "what can you do", "commands"],
                "responses": [
                    "I can help you with various tasks! Try asking me questions about:\n"
                    "- General information\n"
                    "- Text analysis\n"
                    "- Programming concepts\n"
                    "Type 'exit' or 'quit' to end our conversation."
                ]
            },
            "analysis": {
                "patterns": ["analyze", "what is", "tell me about", "explain"],
                "responses": [
                    "I'd be happy to analyze that for you!",
                    "Let me break that down for you.",
                    "Here's what I can tell you about that:"
                ]
            }
        }
    
    def welcome_message(self) -> str:
        """Return a welcome message for the chat assistant."""
        return (
            "🤖 Welcome to CLI Assistant Chat!\n"
            "I'm here to help you with various tasks and questions.\n"
            "Type 'help' to see what I can do, or 'exit'/'quit' to leave.\n"
            "Let's start chatting!"
        )
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text using spaCy NLP capabilities."""
        doc = self.nlp(text.lower())
        
        # Extract entities, tokens, and other linguistic features
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        tokens = [token.text for token in doc if not token.is_space]
        lemmas = [token.lemma_ for token in doc if not token.is_punct and not token.is_space]
        
        return {
            "entities": entities,
            "tokens": tokens,
            "lemmas": lemmas,
            "sentiment": self._analyze_sentiment(doc),
            "keywords": self._extract_keywords(doc)
        }
    
    def _analyze_sentiment(self, doc) -> str:
        """Simple sentiment analysis based on token sentiment."""
        # This is a basic implementation - you might want to use a proper sentiment model
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "love", "like"]
        negative_words = ["bad", "terrible", "awful", "hate", "dislike", "horrible"]
        
        tokens = [token.text.lower() for token in doc]
        positive_count = sum(1 for word in positive_words if word in tokens)
        negative_count = sum(1 for word in negative_words if word in tokens)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _extract_keywords(self, doc) -> List[str]:
        """Extract keywords from the document."""
        keywords = []
        for token in doc:
            if (token.pos_ in ["NOUN", "PROPN", "ADJ"] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2):
                keywords.append(token.lemma_)
        
        return list(set(keywords))  # Remove duplicates
    
    def find_response_category(self, user_input: str) -> Optional[str]:
        """Find the most appropriate response category based on user input."""
        user_input_lower = user_input.lower()
        
        for category, data in self.response_patterns.items():
            for pattern in data["patterns"]:
                if pattern in user_input_lower:
                    return category
        
        return None
    
    def generate_response(self, user_input: str) -> str:
        """Generate a response based on user input."""
        if not user_input.strip():
            return "I didn't catch that. Could you please say something?"
        
        # Check for exit commands
        if any(cmd in user_input.lower() for cmd in ["exit", "quit", "bye", "goodbye"]):
            self.is_running = False
            return self.response_patterns["goodbye"]["responses"][0]
        
        # Find response category
        category = self.find_response_category(user_input)
        
        if category:
            response = self.response_patterns[category]["responses"][0]
            
            # If it's an analysis request, provide text analysis
            if category == "analysis":
                analysis = self.analyze_text(user_input)
                response += f"\n\nText Analysis Results:"
                if analysis["entities"]:
                    response += f"\n📍 Entities found: {', '.join([f'{text} ({label})' for text, label in analysis['entities']])}"
                if analysis["keywords"]:
                    response += f"\n🔑 Keywords: {', '.join(analysis['keywords'])}"
                response += f"\n😊 Sentiment: {analysis['sentiment'].title()}"
            
            return response
        
        # Default response with text analysis
        analysis = self.analyze_text(user_input)
        response = "That's interesting! Let me analyze what you said:\n"
        
        if analysis["keywords"]:
            response += f"\n🔑 I noticed these key concepts: {', '.join(analysis['keywords'][:5])}"
        
        if analysis["entities"]:
            response += f"\n📍 Entities detected: {', '.join([f'{text} ({label})' for text, label in analysis['entities'][:3]])}"
        
        response += f"\n😊 The tone seems {analysis['sentiment']}."
        response += "\n\nIs there anything specific you'd like to know about this topic?"
        
        return response
    
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
