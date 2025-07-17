"""Tests for ChatAssistant with Qwen2 integration."""

import pytest
from unittest.mock import Mock, patch
from src.cli_assistant.chat_assistant import ChatAssistant


class TestChatAssistant:
    """Test cases for ChatAssistant class."""
    
    @patch('src.cli_assistant.chat_assistant.AutoTokenizer')
    @patch('src.cli_assistant.chat_assistant.AutoModelForCausalLM')
    @patch('src.cli_assistant.chat_assistant.pipeline')
    def test_init_success(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test successful initialization of ChatAssistant."""
        # Mock the tokenizer and model
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        mock_pipeline.return_value = Mock()
        
        # Create assistant
        assistant = ChatAssistant()
        
        # Verify initialization
        assert assistant.is_running is True
        assert assistant.conversation_history == []
        assert assistant.system_prompt is not None
        assert "Qwen/Qwen2-0.5B-Instruct" in str(mock_tokenizer.from_pretrained.call_args)
    
    @patch('src.cli_assistant.chat_assistant.AutoTokenizer')
    @patch('src.cli_assistant.chat_assistant.AutoModelForCausalLM')
    @patch('src.cli_assistant.chat_assistant.pipeline')
    def test_welcome_message(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test welcome message generation."""
        # Mock dependencies
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        mock_pipeline.return_value = Mock()
        
        assistant = ChatAssistant()
        message = assistant.welcome_message()
        
        assert "Qwen2" in message
        assert "CLI Assistant" in message
        assert "help" in message.lower()
    
    @patch('src.cli_assistant.chat_assistant.AutoTokenizer')
    @patch('src.cli_assistant.chat_assistant.AutoModelForCausalLM') 
    @patch('src.cli_assistant.chat_assistant.pipeline')
    def test_extract_intent_pattern_matching(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test intent extraction using pattern matching."""
        # Mock dependencies
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        mock_pipeline.return_value = Mock()
        
        assistant = ChatAssistant()
        
        # Test various intents
        assert assistant.extract_intent("add contact") == "add_contact"
        assert assistant.extract_intent("show contacts") == "show_contacts"
        assert assistant.extract_intent("search note") == "search_note"
        assert assistant.extract_intent("help") == "help"
    
    @patch('src.cli_assistant.chat_assistant.AutoTokenizer')
    @patch('src.cli_assistant.chat_assistant.AutoModelForCausalLM')
    @patch('src.cli_assistant.chat_assistant.pipeline')
    def test_conversation_history(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test conversation history management."""
        # Mock dependencies
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        mock_pipeline.return_value = Mock()
        
        assistant = ChatAssistant()
        
        # Add to history
        assistant.add_to_history("Hello", "Hi there!")
        assistant.add_to_history("How are you?", "I'm doing well!")
        
        # Check history
        history = assistant.get_conversation_history()
        assert len(history) == 2
        assert history[0]["user"] == "Hello"
        assert history[0]["assistant"] == "Hi there!"
        assert history[1]["user"] == "How are you?"
        assert history[1]["assistant"] == "I'm doing well!"
    
    @patch('src.cli_assistant.chat_assistant.AutoTokenizer')
    @patch('src.cli_assistant.chat_assistant.AutoModelForCausalLM')
    @patch('src.cli_assistant.chat_assistant.pipeline')
    def test_exit_commands(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test exit command handling."""
        # Mock dependencies
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        mock_pipeline.return_value = Mock()
        
        assistant = ChatAssistant()
        
        # Test exit commands
        response = assistant.generate_response("exit")
        assert "Goodbye" in response
        assert assistant.is_running is False
        
        # Reset for next test
        assistant.is_running = True
        response = assistant.generate_response("quit")
        assert "Goodbye" in response
        assert assistant.is_running is False
    
    @patch('src.cli_assistant.chat_assistant.AutoTokenizer')
    @patch('src.cli_assistant.chat_assistant.AutoModelForCausalLM')
    @patch('src.cli_assistant.chat_assistant.pipeline')
    def test_help_message(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test help message generation."""
        # Mock dependencies
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        mock_pipeline.return_value = Mock()
        
        assistant = ChatAssistant()
        help_msg = assistant.get_help_message()
        
        assert "Contact Commands" in help_msg
        assert "Note Commands" in help_msg
        assert "Qwen2" in help_msg
        assert "AI Features" in help_msg


if __name__ == "__main__":
    pytest.main([__file__])
