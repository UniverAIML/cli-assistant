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

echo 📦 Installing PyInstaller...
python -m pip install pyinstaller

echo 🔨 Building Windows executable...
mkdir "dist\executables" 2>nul
mkdir "build\temp" 2>nul
mkdir "build\specs" 2>nul

pyinstaller --onefile ^
    --name cli-assistant-windows-x64 ^
    --distpath dist\executables ^
    --workpath build\temp ^
    --specpath build\specs ^
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
