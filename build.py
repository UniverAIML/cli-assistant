#!/usr/bin/env python3
"""
B    print("🔧 Creating custom spec file...")ild script for creating executable files from CLI Assistant.
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller

        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Install PyInstaller."""
    print("📦 Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def create_spec_file():
    """Create custom spec file with pathex configuration."""
    print("� Creating custom spec file...")

    # Determine output name based on platform
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        exe_name = f"cli-assistant-{system}-{machine}.exe"
    else:
        exe_name = f"cli-assistant-{system}-{machine}"

    # Get absolute paths and normalize them for Windows
    src_path = os.path.abspath("src").replace("\\", "/")
    cli_assistant_path = os.path.abspath("src/cli_assistant").replace("\\", "/")
    database_path = os.path.abspath("src/cli_assistant/database").replace("\\", "/")
    main_script = os.path.abspath("src/cli_assistant/main.py").replace("\\", "/")

    print(f"📁 Source path: {src_path}")
    print(f"📁 CLI Assistant path: {cli_assistant_path}")
    print(f"📁 Database path: {database_path}")
    print(f"📄 Main script: {main_script}")

    # Create spec file content with improved pathex and hiddenimports
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{main_script}'],
    pathex=[
        '{src_path}',
        '{cli_assistant_path}',
        '{database_path}',
    ],
    binaries=[],
    datas=[],
    hiddenimports=[
        'cli_assistant',
        'cli_assistant.main',
        'cli_assistant.__main__',
        'cli_assistant.operations_manager',
        'cli_assistant.chat_assistant',
        'cli_assistant.interactive_menu',
        'cli_assistant.model_manager',
        'cli_assistant.function_executor',
        'cli_assistant.config_manager',
        'cli_assistant.function_definitions',
        'cli_assistant.database',
        'cli_assistant.database.__init__',
        'cli_assistant.database.data_manager',
        'cli_assistant.database.contact_models',
        'cli_assistant.database.note_models',
        # Third-party imports
        'questionary',
        'rich',
        'rich.console',
        'rich.table',
        'rich.panel',
        'colorama',
        'tabulate',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{exe_name.replace('.exe', '')}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

    # Write spec file
    spec_filename = f"build/specs/{exe_name.replace('.exe', '')}.spec"
    os.makedirs(os.path.dirname(spec_filename), exist_ok=True)

    with open(spec_filename, "w", encoding="utf-8") as f:
        f.write(spec_content)

    print(f"✅ Spec file created: {spec_filename}")
    return spec_filename, exe_name


def build_executable():
    """Build executable file using custom spec."""
    print("🔨 Building executable...")

    # Create spec file
    spec_filename, exe_name = create_spec_file()

    # PyInstaller command with spec file
    cmd = [
        "pyinstaller",
        "--distpath",
        "dist/executables",
        "--workpath",
        "build/temp",
        spec_filename,
    ]

    print(f"🚀 Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)

    return exe_name


def main():
    """Main build function."""
    print("🏗️  CLI Assistant Build Script")
    print("=" * 40)

    # Check if we're in the right directory
    if not os.path.exists("pyproject.toml"):
        print("❌ Error: pyproject.toml not found!")
        print("   Please run this script from the project root.")
        sys.exit(1)

    # Check PyInstaller
    if not check_pyinstaller():
        install_pyinstaller()

    # Create directories
    os.makedirs("dist/executables", exist_ok=True)
    os.makedirs("build/temp", exist_ok=True)
    os.makedirs("build/specs", exist_ok=True)

    try:
        exe_name = build_executable()

        # Check if file was created
        exe_path = Path("dist/executables") / exe_name
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ Successfully built: {exe_path}")
            print(f"📏 File size: {file_size:.1f} MB")
            print(f"🎯 Platform: {platform.system()} {platform.machine()}")
        else:
            print(f"❌ Build failed: {exe_path} not found")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

    print("\n🎉 Build completed successfully!")
    print(f"📦 Executable location: dist/executables/{exe_name}")


if __name__ == "__main__":
    main()
