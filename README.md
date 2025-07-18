# CLI Assistant

Сучасний CLI асистент з AI-чат можливостями для робочих процесів розробки.

## 🚀 Особливості

- **AI-Powered Chat**: Інтелектуальний чат-асистент з підтримкою виклику функцій
- **Управління контактами**: Повний CRUD для контактів з валідацією
- **Управління нотатками**: Створення, пошук та редагування нотаток з тегами
- **Красиве меню**: Інтерактивне меню з кольоровим форматуванням
- **OpenAI Integration**: Підтримка OpenAI API для розумних відповідей

## 🖥️ Встановлення

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
