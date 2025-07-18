#!/bin/bash
# Build script for CLI Assistant (Linux/macOS)

set -e

echo "🏗️  CLI Assistant Build Script (Unix)"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found!"
    echo "   Please run this script from the project root."
    exit 1
fi

# Determine platform and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

# Normalize platform names
case $OS in
    darwin)
        OS="macos"
        ;;
    mingw64_nt-*|cygwin_nt-*|msys_nt-*)
        OS="windows"
        ;;
esac

# Normalize architecture names
case $ARCH in
    x86_64)
        ARCH="x64"
        ;;
    arm64)
        ARCH="arm64"
        ;;
    aarch64)
        ARCH="arm64"
        ;;
esac

EXE_NAME="cli-assistant-${OS}-${ARCH}"

echo "🎯 Building for: ${OS} ${ARCH}"

# Choose the right Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python not found!"
    exit 1
fi

echo "� Using Python: $PYTHON_CMD"

echo "�📦 Installing PyInstaller..."
$PYTHON_CMD -m pip install pyinstaller

echo "🔨 Building executable..."
mkdir -p "dist/executables"
mkdir -p "build/temp" 
mkdir -p "build/specs"

# Additional flags for macOS
EXTRA_FLAGS=""
if [ "$(uname -s)" = "Darwin" ]; then
    EXTRA_FLAGS="--osx-bundle-identifier com.univer.cli-assistant --icon $(pwd)/src/cli_assistant/icon.png"
else
    EXTRA_FLAGS="--icon $(pwd)/src/cli_assistant/icon.png"
fi

pyinstaller --onefile \
    --name "$EXE_NAME" \
    --distpath "dist/executables" \
    --workpath "build/temp" \
    --specpath "build/specs" \
    $EXTRA_FLAGS \
    "src/cli_assistant/main.py"

if [ -f "dist/executables/$EXE_NAME" ]; then
    # Make executable
    chmod +x "dist/executables/$EXE_NAME"
    
    # Get file size
    size=$(stat -f%z "dist/executables/$EXE_NAME" 2>/dev/null || stat -c%s "dist/executables/$EXE_NAME" 2>/dev/null)
    size_mb=$((size / 1048576))
    
    echo "✅ Successfully built: dist/executables/$EXE_NAME"
    echo "📏 File size: ${size_mb} MB"
    echo "🎯 Platform: ${OS} ${ARCH}"
    echo ""
    echo "🎉 Build completed successfully!"
    echo "📦 Executable location: dist/executables/$EXE_NAME"
else
    echo "❌ Build failed: executable not found"
    exit 1
fi
