#!/usr/bin/env python3
"""
Setup script for CLI Assistant package.
"""

from setuptools import setup, find_packages
import os


# Читаємо версію з __init__.py
def get_version():
    with open(
        os.path.join("src", "cli_assistant", "__init__.py"), "r", encoding="utf-8"
    ) as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"


# Читаємо опис з README
def get_long_description():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()


setup(
    name="cli-assistant",
    version=get_version(),
    description="AI-powered CLI assistant for managing contacts and notes",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Univer AI ML",
    author_email="info@univer.ai",
    url="https://github.com/UniverAIML/cli-assistant",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.9,<3.14",
    install_requires=[
        "openai>=1.97.0,<2.0.0",
        "colorama>=0.4.6,<0.5.0",
        "questionary>=2.0.0,<3.0.0",
        "rich>=13.0.0,<14.0.0",
        "tabulate>=0.9.0,<1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.0.0",
            "black>=24.0.0",
            "isort>=5.13.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "types-colorama>=0.4.15.20240311",
        ],
    },
    entry_points={
        "console_scripts": [
            "cli-assistant=cli_assistant.main:main",
            "cli-assistant-chat=cli_assistant.main:main_chat",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Groupware",
        "Topic :: Communications :: Chat",
    ],
    keywords="cli assistant ai contacts notes management",
    project_urls={
        "Bug Reports": "https://github.com/UniverAIML/cli-assistant/issues",
        "Source": "https://github.com/UniverAIML/cli-assistant",
        "Documentation": "https://github.com/UniverAIML/cli-assistant/blob/main/README.md",
    },
)
