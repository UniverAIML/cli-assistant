# CLI Assistant

A CLI assistant tool for development workflows.

## Installation

```bash
# Install dependencies
poetry install
```

## Activating Virtual Environment

In Poetry 2.x, there are several ways to work with the virtual environment:

### Option 1: Use poetry run (Recommended)
```bash
# Run commands directly with poetry run
poetry run cli-assistant
poetry run python src/cli_assistant/main.py
```

### Option 2: Manual activation
```bash
# Get activation command for your shell
poetry env activate

# On Windows PowerShell, use the output like:
# & "C:\path\to\venv\Scripts\Activate.ps1"

# On Linux/macOS:
# eval $(poetry env activate)
```

### Option 3: Install shell plugin (Optional)
```bash
# Install the shell plugin to restore poetry shell command
poetry self add poetry-plugin-shell

# Then you can use:
poetry shell
```

## Usage

```bash
# Run the CLI tool
poetry run cli-assistant

# Run Python directly
poetry run python src/cli_assistant/main.py

# Run with arguments
poetry run cli-assistant --help
```

## Development

### Code Quality Tools
```bash
# Run tests
poetry run pytest

# Run tests with verbose output
poetry run pytest -v

# Format code with Black
poetry run black .

# Sort imports with isort
poetry run isort .

# Lint code with flake8
poetry run flake8

# Type checking with mypy
poetry run mypy src/
```

### Environment Management
```bash
# Show virtual environment info
poetry env info

# Show path to virtual environment
poetry env info --path

# Show path to Python executable
poetry env info --executable

# List all environments for this project
poetry env list

# Remove virtual environment
poetry env remove python
```

### VS Code Tasks
The project includes VS Code tasks for common operations:
- **Install Dependencies**: `Ctrl+Shift+P` → "Tasks: Run Task" → "Install Dependencies"
- **Run CLI Assistant**: `Ctrl+Shift+P` → "Tasks: Run Task" → "Run CLI Assistant"
- **Run Tests**: `Ctrl+Shift+P` → "Tasks: Run Task" → "Run Tests"
- **Format Code**: `Ctrl+Shift+P` → "Tasks: Run Task" → "Format Code"
- **Check Types**: `Ctrl+Shift+P` → "Tasks: Run Task" → "Check Types"

## Project Structure

```
cli-assistant/
├── src/
│   └── cli_assistant/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── docs/
├── pyproject.toml
└── README.md
```