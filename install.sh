#!/bin/bash
# Installation script for CLI Assistant as a global package

set -e

echo "🚀 Installing CLI Assistant..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install Poetry first:"
    echo "curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Check if we're in the correct directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ pyproject.toml not found. Run this script from the project root folder."
    exit 1
fi

echo "📦 Installing dependencies..."
poetry install

echo "🔨 Building package..."
poetry build

echo "📥 Installing package globally..."
poetry install

echo "🔧 Environment variables setup..."
echo ""
echo "For OpenAI API usage (optional):"
echo "1. Get API key from https://platform.openai.com/api-keys"
echo "2. Set environment variables:"
echo ""
echo "   export USE_OPENAI=\"true\""
echo "   export OPENAI_API_KEY=\"your-api-key-here\""
echo "   export OPENAI_MODEL=\"gpt-4o-mini\""
echo ""

read -p "Would you like to configure OpenAI now? (y/N): " setup_openai
if [[ "$setup_openai" =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Enter your OpenAI API key: " api_key
    if [ ! -z "$api_key" ]; then
        # Add to .bashrc or .zshrc
        shell_config=""
        if [ -f "$HOME/.zshrc" ]; then
            shell_config="$HOME/.zshrc"
        elif [ -f "$HOME/.bashrc" ]; then
            shell_config="$HOME/.bashrc"
        fi
        
        if [ ! -z "$shell_config" ]; then
            echo "" >> "$shell_config"
            echo "# CLI Assistant OpenAI Configuration" >> "$shell_config"
            echo "export USE_OPENAI=\"true\"" >> "$shell_config"
            echo "export OPENAI_API_KEY=\"$api_key\"" >> "$shell_config"
            echo "export OPENAI_MODEL=\"gpt-4o-mini\"" >> "$shell_config"
            echo "✅ OpenAI API configured in $shell_config!"
            echo "⚠️  Restart terminal or run: source $shell_config"
        else
            echo "❌ Could not find .bashrc or .zshrc. Please add variables manually."
        fi
    else
        echo "❌ API key not entered. Configuration skipped."
    fi
else
    echo "ℹ️  OpenAI configuration skipped. Local model will be used."
fi

echo ""
echo "🔧 Additional configuration (optional):"
echo "   export CLI_ASSISTANT_DATA_DIR=\"\$HOME/Documents/CLIAssistant\""
echo "   export CLI_ASSISTANT_LOG_LEVEL=\"INFO\""
echo ""

echo "✅ Installation completed!"
echo ""
echo "🎉 You can now use CLI Assistant from anywhere:"
echo "   cli-assistant           # Interactive menu"
echo "   cli-assistant chat      # AI chat assistant"
echo "   cli-assistant --help    # Help information"
echo ""
echo "📚 For detailed information see INSTALL.md"
