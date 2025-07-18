# CLI Assistant

A modern CLI assistant tool with AI-powered chat capabilities for development workflows.

## 🖥️ Platform Support & Installation

This CLI Assistant supports hardware acceleration on different platforms with automatic detection and optimization.

### Prerequisites
- Python 3.9-3.13
- Poetry (for dependency management)
- For GPU acceleration:
  - Windows/Linux: NVIDIA GPU with CUDA support
  - macOS: Apple Silicon (M1/M2/M3/M4) for MPS acceleration

### Install Dependencies
```bash
# Install all dependencies with Poetry
poetry install

# Verify installation
poetry run cli-assistant --help
```

### Automatic Platform Detection
The application automatically detects your platform and configures optimal acceleration:
- **Windows/Linux + NVIDIA**: Uses CUDA acceleration
- **macOS Apple Silicon**: Uses Metal Performance Shaders (MPS)
- **Other platforms**: Falls back to CPU mode

## 🎯 Quick Start

```bash
# Start the AI chat assistant
poetry run cli-assistant
```
## 📁 Project Structure

```
cli-assistant/
├── src/
│   ├── cli_assistant/              # Main application
│   │   ├── main.py                 # Entry point
│   │   ├── chat_assistant.py       # AI chat functionality
│   │   ├── function_definitions.py # AI function definitions
│   │   └── assistant_stub.py       # Core business logic
│   ├── address_book/               # Contact management
│   │   ├── class_addressBook.py    # Address book implementation
│   │   ├── class_record_main.py    # Contact record model
│   │   ├── base_field_classes.py   # Field validation classes
│   │   └── class_birthday_managment.py # Birthday functionality
│   └── notes_models/               # Note management (future)
├── tests/                          # Test suite
├── docs/                           # Documentation
├── pyproject.toml                  # Project configuration
└── README.md                       # This file
```

## 🤖 AI Features

- **Function Calling**: AI can execute specific functions based on user intent
- **Context Awareness**: Maintains conversation history for better responses
- **Multi-Platform Optimization**: Automatic hardware detection and optimization

## 🚨 Troubleshooting

### GPU Not Detected
- **Windows**: Ensure NVIDIA drivers are updated, run `nvidia-smi`
- **macOS**: Check MPS availability: `python -c "import torch; print(torch.backends.mps.is_available())"`
- **Linux**: Verify CUDA installation and drivers

### Windows CUDA Issues
- Ensure NVIDIA drivers are up to date
- Check CUDA version compatibility
- Run `nvidia-smi` to verify GPU visibility

### macOS MPS Issues
- Requires macOS 12.3+
- Check with: `python -c "import torch; print(torch.backends.mps.is_available())"`


# Example environment configuration for CLI Assistant

# =============================================================================
# AI Provider Configuration
# =============================================================================
# Choose AI provider: "local" or "openai"
USE_OPENAI=true

# =============================================================================
# OpenAI Configuration (only used when USE_OPENAI=true)
# =============================================================================
OPENAI_API_KEY=API_KEY
OPENAI_MODEL=gpt-4.1
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.1
OPENAI_TOP_P=1.0
OPENAI_TIMEOUT=30

# Available OpenAI models:
# - gpt-3.5-turbo (fast, cheap)
# - gpt-4 (high quality)
# - gpt-4-turbo (balanced)
# - gpt-4o (latest)

# =============================================================================
# Local Model Configuration (used when USE_OPENAI=false)
# =============================================================================
# These are handled by the existing config_manager.py
# Local model will be automatically detected based on your hardware:
# - Windows/Linux + NVIDIA GPU: Uses CUDA acceleration
# - macOS Apple Silicon: Uses MPS acceleration  
# - Other platforms: Falls back to CPU mode

# =============================================================================
# Usage Examples:
# =============================================================================
# For OpenAI API:
# 1. Set USE_OPENAI=true
# 2. Set your OPENAI_API_KEY
# 3. Choose OPENAI_MODEL
# 4. Run: poetry run cli-assistant

# For local models:
# 1. Set USE_OPENAI=false (default)
# 2. Run: poetry run cli-assistant
