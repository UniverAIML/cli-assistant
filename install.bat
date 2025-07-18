@echo off
setlocal enabledelayedexpansion
REM Installation script for CLI Assistant as a global package on Windows

echo 🚀 Installing CLI Assistant...

REM Check if Poetry is installed
poetry --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Poetry not found. Please install Poetry first:
    echo https://python-poetry.org/docs/#installation
    exit /b 1
)

REM Check if we're in the correct directory
if not exist "pyproject.toml" (
    echo ❌ pyproject.toml not found. Run this script from the project root folder.
    exit /b 1
)

echo 📦 Installing dependencies...
poetry install

echo 🔨 Building package...
poetry build

echo 📥 Installing package globally...
poetry install

echo 🔧 Environment variables setup...
echo.
echo For OpenAI API usage (optional):
echo 1. Get API key from https://platform.openai.com/api-keys
echo 2. Set environment variables:
echo.
echo    setx USE_OPENAI "true"
echo    setx OPENAI_API_KEY "your-api-key-here"
echo    setx OPENAI_MODEL "gpt-4o-mini"
echo.
set /p setup_openai="Would you like to configure OpenAI now? (y/N): "
if /i "%setup_openai%"=="y" (
    echo.
    set /p api_key="Enter your OpenAI API key: "
    if not "!api_key!"=="" (
        setx USE_OPENAI "true"
        setx OPENAI_API_KEY "!api_key!"
        setx OPENAI_MODEL "gpt-4o-mini"
        echo ✅ OpenAI API configured!
        echo ⚠️  Restart terminal to apply changes.
    ) else (
        echo ❌ API key not entered. Configuration skipped.
    )
) else (
    echo ℹ️  OpenAI configuration skipped. Local model will be used.
)

echo.
echo 🔧 Additional configuration (optional):
echo    setx CLI_ASSISTANT_DATA_DIR "C:\Users\%USERNAME%\Documents\CLIAssistant"
echo    setx CLI_ASSISTANT_LOG_LEVEL "INFO"
echo.

echo ✅ Installation completed!
echo.
echo 🎉 You can now use CLI Assistant from anywhere:
echo    cli-assistant           # Interactive menu
echo    cli-assistant chat      # AI chat assistant
echo    cli-assistant --help    # Help information
echo.
echo 📚 For detailed information see INSTALL.md
