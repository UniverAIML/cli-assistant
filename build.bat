@echo off
setlocal enabledelayedexpansion

echo 🏗️  CLI Assistant Build Script (Windows)
echo ===============================================

REM Check if we're in the right directory
if not exist "pyproject.toml" (
    echo ❌ Error: pyproject.toml not found!
    echo    Please run this script from the project root.
    exit /b 1
)

REM Determine Python command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
    ) else (
        echo ❌ Error: Python not found!
        exit /b 1
    )
)

echo 🐍 Using Python: %PYTHON_CMD%

echo 📦 Installing PyInstaller...
%PYTHON_CMD% -m pip install pyinstaller

echo 🔨 Building Windows executable...
mkdir "dist\executables" 2>nul
mkdir "build\temp" 2>nul
mkdir "build\specs" 2>nul

pyinstaller --onefile ^
    --name cli-assistant-windows-x64 ^
    --distpath dist\executables ^
    --workpath build\temp ^
    --specpath build\specs ^
    --icon %cd%\src\cli_assistant\icon.ico ^
    --hidden-import=colorama ^
    --hidden-import=openai ^
    --hidden-import=questionary ^
    --hidden-import=rich ^
    --hidden-import=tabulate ^
    --hidden-import=textual ^
    --hidden-import=pyfiglet ^
    --hidden-import=halo ^
    --hidden-import=tqdm ^
    --hidden-import=art ^
    --hidden-import=cli_assistant.chat_assistant ^
    --hidden-import=cli_assistant.interactive_menu ^
    --hidden-import=cli_assistant.config_manager ^
    --hidden-import=cli_assistant.function_definitions ^
    --hidden-import=cli_assistant.function_executor ^
    --hidden-import=cli_assistant.model_manager ^
    --hidden-import=cli_assistant.operations_manager ^
    --hidden-import=cli_assistant.database.data_manager ^
    --hidden-import=cli_assistant.database.contact_models ^
    --hidden-import=cli_assistant.database.note_models ^
    src\cli_assistant\main.py

if exist "dist\executables\cli-assistant-windows-x64.exe" (
    echo ✅ Successfully built: dist\executables\cli-assistant-windows-x64.exe
    for %%A in ("dist\executables\cli-assistant-windows-x64.exe") do (
        set size=%%~zA
        set /a size_mb=!size! / 1048576
        echo 📏 File size: !size_mb! MB
    )
    echo 🎯 Platform: Windows x64
    echo.
    echo 🎉 Build completed successfully!
    echo 📦 Executable location: dist\executables\cli-assistant-windows-x64.exe
) else (
    echo ❌ Build failed: executable not found
    exit /b 1
)

pause
