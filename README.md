# CLI Assistant

[![Tests](https://github.com/UniverAIML/cli-assistant/actions/workflows/tests.yml/badge.svg)](https://github.com/UniverAIML/cli-assistant/actions/workflows/tests.yml)
[![Lint](https://github.com/UniverAIML/cli-assistant/actions/workflows/lint.yml/badge.svg)](https://github.com/UniverAIML/cli-assistant/actions/workflows/lint.yml)
[![Build and Release](https://github.com/UniverAIML/cli-assistant/actions/workflows/build-and-release.yml/badge.svg)](https://github.com/UniverAIML/cli-assistant/actions/workflows/build-and-release.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Сучасний CLI асистент з AI-чат можливостями для робочих процесів розробки.

## 🚀 Особливості

- **AI-Powered Chat**: Інтелектуальний чат-асистент з підтримкою виклику функцій
- **Управління контактами**: Повний CRUD для контактів з валідацією
- **Управління нотатками**: Створення, пошук та редагування нотаток з тегами
- **Красиве меню**: Інтерактивне меню з кольоровим форматуванням
- **OpenAI Integration**: Підтримка OpenAI API для розумних відповідей

## � Завантаження

### Готові виконувані файли
[![Latest Release](https://img.shields.io/github/v/release/UniverAIML/cli-assistant)](https://github.com/UniverAIML/cli-assistant/releases/latest)
[![Download Count](https://img.shields.io/github/downloads/UniverAIML/cli-assistant/total)](https://github.com/UniverAIML/cli-assistant/releases)

Завантажте готовий виконуваний файл для вашої операційної системи:

- **Windows x64**: `cli-assistant-windows-x64.exe`
- **Linux x64**: `cli-assistant-linux-x64`
- **macOS Intel**: `cli-assistant-macos-x64`
- **macOS Apple Silicon**: `cli-assistant-macos-arm64`

[👉 Завантажити останню версію](https://github.com/UniverAIML/cli-assistant/releases/latest)

## �🖥️ Встановлення

### Вимоги
- Python 3.9-3.13
- Poetry (для управління залежностями)
- OpenAI API ключ

### Встановлення залежностей
```bash
# Встановлюємо всі залежності через Poetry
poetry install

# Перевіряємо встановлення
poetry run cli-assistant --help
```

### Конфігурація OpenAI
```bash
# Встановлюємо змінні оточення
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_MODEL="gpt-4o-mini"
```

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
│   │   ├── model_manager.py        # Управління OpenAI API
│   │   ├── config_manager.py       # Управління конфігурацією
│   │   ├── operations_manager.py   # Бізнес-логіка операцій
│   │   ├── function_executor.py    # Виконавець функцій
│   │   └── interactive_menu.py     # Інтерактивне меню
│   └── database/                   # Моделі даних
│       ├── contact_models.py       # Моделі контактів
│       ├── note_models.py          # Моделі нотаток
│       └── data_manager.py         # Управління даними
├── tests/                          # Тести
├── pyproject.toml                  # Конфігурація Poetry
└── README.md                       # Ця документація
```

## 🤖 OpenAI Features

- **Function Calling**: AI може виконувати специфічні функції на основі наміру користувача
- **Context Awareness**: Зберігає історію розмови для кращих відповідей
- **GPT Models**: Підтримка різних моделей GPT (3.5-turbo, 4, 4o-mini)

## 🚨 Troubleshooting

### API Key Issues
- Перевірте, що встановлена змінна `OPENAI_API_KEY`
- Переконайтеся, що API ключ дійсний та має достатньо кредитів

### Model Access
- Переконайтеся, що ваш акаунт має доступ до обраної моделі


## 🌟 Environment Configuration

```bash
# OpenAI Configuration
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_MODEL="gpt-4o-mini"
export OPENAI_MAX_TOKENS=1000
export OPENAI_TEMPERATURE=0.1

# Available OpenAI models:
# - gpt-3.5-turbo (fast, cheap)
# - gpt-4 (high quality)
# - gpt-4-turbo (balanced)
# - gpt-4o-mini (latest, cost-effective)
```

## 🚀 Usage Examples

```bash
# Run interactive menu
poetry run cli-assistant

# Run direct chat
poetry run cli-assistant-chat

# With custom model
OPENAI_MODEL="gpt-4" poetry run cli-assistant
```

## 🛠️ Розробка

### Статус збірки

| Платформа | Статус |
|-----------|--------|
| **Tests** | [![Tests](https://github.com/UniverAIML/cli-assistant/actions/workflows/tests.yml/badge.svg)](https://github.com/UniverAIML/cli-assistant/actions/workflows/tests.yml) |
| **Linting** | [![Lint](https://github.com/UniverAIML/cli-assistant/actions/workflows/lint.yml/badge.svg)](https://github.com/UniverAIML/cli-assistant/actions/workflows/lint.yml) |
| **Build & Release** | [![Build and Release](https://github.com/UniverAIML/cli-assistant/actions/workflows/build-and-release.yml/badge.svg)](https://github.com/UniverAIML/cli-assistant/actions/workflows/build-and-release.yml) |

### Локальна збірка

```bash
# Збірка для Windows
build.bat

# Збірка для Linux/macOS  
./build.sh

# Встановити залежності
poetry install

# Запустити тести
poetry run pytest -v

# Перевірка типів
poetry run mypy src/

# Форматування коду
poetry run black .
```

### Технології

- **Python 3.9-3.13**: Основна мова розробки
- **Poetry**: Управління залежностями
- **PyInstaller**: Створення виконуваних файлів
- **GitHub Actions**: CI/CD pipeline
- **OpenAI API**: AI функціональність
