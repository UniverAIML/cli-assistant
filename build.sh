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

echo "📦 Installing PyInstaller..."
python3 -m pip install pyinstaller

echo "🔨 Building executable..."
mkdir -p "dist/executables"
mkdir -p "build/temp" 
mkdir -p "build/specs"

pyinstaller --onefile \
    --name "$EXE_NAME" \
    --distpath "dist/executables" \
    --workpath "build/temp" \
    --specpath "build/specs" \
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
