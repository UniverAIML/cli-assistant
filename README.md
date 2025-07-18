# CLI Assistant

Сучасний CLI асистент з AI-чат можливостями для робочих процесів розробки.

## 🚀 Особливості

- **AI-Powered Chat**: Інтелектуальний чат-асистент з підтримкою виклику функцій
- **Управління контактами**: Повний CRUD для контактів з валідацією
- **Управління нотатками**: Створення, пошук та редагування нотаток з тегами
- **Красиве меню**: Інтерактивне меню з кольоровим форматуванням
- **Гнучкі AI моделі**: Підтримка локальних моделей та OpenAI API
- **Автоматична оптимізація**: Автоматичне визначення платформи та прискорення

## 🖥️ Підтримка платформ та встановлення

Цей CLI асистент підтримує апаратне прискорення на різних платформах з автоматичним визначенням та оптимізацією.

### Вимоги
- Python 3.9-3.13
- Poetry (для управління залежностями)
- Для GPU прискорення:
  - Windows/Linux: NVIDIA GPU з підтримкою CUDA
  - macOS: Apple Silicon (M1/M2/M3/M4) для MPS прискорення

### Встановлення залежностей
```bash
# Встановлюємо всі залежності через Poetry
poetry install

# Перевіряємо встановлення
poetry run cli-assistant --help
```

### Автоматичне визначення платформи
Додаток автоматично визначає вашу платформу та налаштовує оптимальне прискорення:
- **Windows/Linux + NVIDIA**: Використовує CUDA прискорення
- **macOS Apple Silicon**: Використовує Metal Performance Shaders (MPS)
- **Інші платформи**: Повертається до CPU режиму

## 🎯 Швидкий старт

```bash
# Запуск AI чат-асистента
poetry run cli-assistant
```

## 📁 Структура проекту

```
cli-assistant/
├── src/
│   ├── cli_assistant/              # Основний додаток
│   │   ├── main.py                 # Точка входу
│   │   ├── chat_assistant.py       # AI чат функціональність
│   │   ├── function_definitions.py # Визначення AI функцій
│   │   ├── model_manager.py        # Управління AI моделями
│   │   ├── config_manager.py       # Управління конфігурацією
│   │   ├── operations_manager.py   # Бізнес-логіка операцій
│   │   ├── function_executor.py    # Виконавець функцій
│   │   └── interactive_menu.py     # Інтерактивне меню
│   ├── database/                   # Моделі даних
│   │   ├── contact_models.py       # Моделі контактів
│   │   ├── note_models.py          # Моделі нотаток
│   │   └── data_manager.py         # Управління даними
│   └── personal_assistant.py       # Основний клас асистента
├── tests/                          # Тести
├── models/                         # Локальні AI моделі
├── pyproject.toml                  # Конфігурація Poetry
└── README.md                       # Ця документація
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
# Hugging Face Token
HF_TOKEN=API_KEY

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
