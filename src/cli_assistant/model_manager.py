"""
Управління моделями ШІ та стратегії генерації відповідей.
Цей модуль містить класи для роботи з різними типами AI моделей:
- Локальні моделі (Qwen, Mistral та інші)
- API моделі (OpenAI GPT)
"""

# Імпорт бібліотек для роботи з абстрактними класами та типізацією
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, cast, Literal
from typing_extensions import TypedDict

# Стандартні бібліотеки Python
import os
import json

# Бібліотека для роботи з OpenAI API
import openai
from openai.types.chat import ChatCompletionMessageParam

# Локальні імпорти з нашого проекту
from .config_manager import ConfigurationManager, LoggerMixin
from .function_definitions import FunctionDefinitions


# Визначення типів повідомлень для чату з використанням TypedDict
# TypedDict дозволяє створити типізовані словники з фіксованою структурою


class SystemMessage(TypedDict):
    """Системне повідомлення - задає контекст та правила для AI"""

    role: Literal["system"]  # Роль завжди "system"
    content: str  # Текст системного повідомлення


class UserMessage(TypedDict):
    """Повідомлення від користувача"""

    role: Literal["user"]  # Роль завжди "user"
    content: str  # Текст повідомлення користувача


class AssistantMessage(TypedDict):
    """Звичайне повідомлення від асистента без виклику функцій"""

    role: Literal["assistant"]  # Роль завжди "assistant"
    content: Optional[str]  # Текст відповіді асистента (може бути None)


class AssistantToolCallMessage(TypedDict):
    """Повідомлення від асистента з викликом функцій/інструментів"""

    role: Literal["assistant"]  # Роль завжди "assistant"
    content: Optional[
        str
    ]  # Текст відповіді (може бути None якщо тільки виклик функції)
    tool_calls: List[Dict[str, Any]]  # Список викликів функцій з параметрами


class ToolMessage(TypedDict):
    """Повідомлення з результатом виконання функції/інструменту"""

    role: Literal["tool"]  # Роль завжди "tool"
    tool_call_id: str  # ID виклику функції для зв'язку з запитом
    name: str  # Назва функції що була виконана
    content: str  # Результат виконання функції


# Об'єднуючий тип для всіх можливих типів повідомлень у чаті
MessageType = Union[
    SystemMessage, UserMessage, AssistantMessage, AssistantToolCallMessage, ToolMessage
]


class ResponseStrategy(ABC):
    """
    Абстрактний клас для стратегій генерації відповідей.
    Використовується паттерн "Стратегія" для підтримки різних способів генерації відповідей:
    - Локальні моделі (Qwen, Mistral)
    - API моделі (OpenAI GPT)
    """

    @abstractmethod
    def generate_response(
        self, model: Any, tokenizer: Any, messages: List[Dict[str, Any]], **kwargs: Any
    ) -> str:
        """
        Генерує відповідь використовуючи конкретну стратегію.

        Args:
            model: Модель ШІ для генерації тексту
            tokenizer: Токенізатор для обробки тексту
            messages: Список повідомлень для контексту
            **kwargs: Додаткові параметри генерації

        Returns:
            str: Згенерована відповідь
        """
        pass


class FunctionCallingStrategy(ResponseStrategy):
    """
    Стратегія для генерації відповідей з можливістю виклику функцій.
    Використовується для локальних моделей (Qwen, Mistral та інших).
    """

    def generate_response(
        self, model: Any, tokenizer: Any, messages: List[Dict[str, Any]], **kwargs: Any
    ) -> str:
        """
        Генерує відповідь з можливістю виклику функцій для локальних моделей.

        Процес:
        1. Підготовка повідомлень за допомогою chat template
        2. Токенізація тексту
        3. Генерація відповіді моделлю
        4. Декодування результату

        Args:
            model: Завантажена локальна модель
            tokenizer: Токенізатор для цієї моделі
            messages: Історія розмови та контекст
            **kwargs: Параметри генерації (temperature, max_tokens тощо)

        Returns:
            str: Згенерована відповідь або виклик функції
        """
        # Застосовуємо chat template для форматування повідомлень
        # add_generation_prompt=True додає спеціальні токени для початку генерації
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        # Токенізуємо текст та переносимо на GPU якщо доступно
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        # Отримуємо параметри генерації з конфігурації
        generation_kwargs = kwargs.get("generation_kwargs", {})
        # Встановлюємо pad_token_id якщо не задано, щоб уникнути попереджень
        generation_kwargs.setdefault("pad_token_id", tokenizer.eos_token_id)

        # Генеруємо відповідь за допомогою моделі
        generated_ids = model.generate(**model_inputs, **generation_kwargs)

        # Видаляємо вхідні токени, залишаємо тільки згенеровані
        # Це потрібно щоб отримати тільки нову частину відповіді
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        # Декодуємо токени назад у текст
        # skip_special_tokens=True видаляє службові токени
        response: str = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[
            0
        ]
        return response


class OpenAIStrategy(ResponseStrategy):
    """
    Стратегія для генерації відповідей через OpenAI API.
    Використовується для роботи з моделями GPT-3.5, GPT-4 та іншими.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Ініціалізує OpenAI стратегію.

        Args:
            api_key: API ключ OpenAI (якщо не вказано, береться з змінної оточення)
            model: Назва моделі OpenAI для використання
        """
        # Використовуємо API ключ з параметра, змінної оточення або викидаємо помилку
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.model_name = model
        # Створюємо клієнт OpenAI для API викликів
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_response(
        self,
        model: Any,  # Не використовується для OpenAI, але зберігається для сумісності
        tokenizer: Any,  # Не використовується для OpenAI, але зберігається для сумісності
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """
        Генерує відповідь використовуючи OpenAI API.

        Args:
            model: Не використовується (для сумісності з інтерфейсом)
            tokenizer: Не використовується (для сумісності з інтерфейсом)
            messages: Список повідомлень для контексту
            **kwargs: Додаткові параметри (max_tokens, temperature тощо)

        Returns:
            str: Відповідь від OpenAI або інформація про виклик функції
        """
        try:
            # Перевіряємо, чи ініціалізований клієнт OpenAI
            if not self.client:
                raise RuntimeError("OpenAI client not initialized")

            # Імпортуємо визначення функцій
            from .function_definitions import FunctionDefinitions

            # Конвертуємо наші функції у формат OpenAI tools
            tools = []
            for func_name, func_def in FunctionDefinitions.AVAILABLE_FUNCTIONS.items():
                tool = {
                    "type": "function",
                    "function": {
                        "name": func_def["name"],
                        "description": func_def["description"],
                        "parameters": func_def["parameters"],
                    },
                }
                tools.append(tool)

            # Створюємо completion з підтримкою виклику функцій
            # Конвертуємо повідомлення у правильний формат OpenAI
            openai_messages: List[ChatCompletionMessageParam] = []
            for msg in messages:
                if msg["role"] == "system":
                    # Системне повідомлення
                    openai_messages.append(
                        cast(
                            ChatCompletionMessageParam,
                            {"role": "system", "content": msg["content"]},
                        )
                    )
                elif msg["role"] == "user":
                    # Повідомлення користувача
                    openai_messages.append(
                        cast(
                            ChatCompletionMessageParam,
                            {"role": "user", "content": msg["content"]},
                        )
                    )
                elif msg["role"] == "assistant":
                    if "tool_calls" in msg:
                        # Повідомлення асистента з викликом функцій
                        openai_messages.append(
                            cast(
                                ChatCompletionMessageParam,
                                {
                                    "role": "assistant",
                                    "content": msg.get("content"),
                                    "tool_calls": msg["tool_calls"],
                                },
                            )
                        )
                    else:
                        # Звичайне повідомлення асистента
                        openai_messages.append(
                            cast(
                                ChatCompletionMessageParam,
                                {"role": "assistant", "content": msg["content"]},
                            )
                        )
                elif msg["role"] == "tool":
                    # Повідомлення з результатом виконання функції
                    openai_messages.append(
                        cast(
                            ChatCompletionMessageParam,
                            {
                                "role": "tool",
                                "tool_call_id": msg["tool_call_id"],
                                "name": msg["name"],
                                "content": msg["content"],
                            },
                        )
                    )

            # Створюємо API виклик з правильними параметрами
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,  # type: ignore
                tools=tools,  # type: ignore
                tool_choice="auto",  # Автоматично вибирати чи викликати функцію
                max_tokens=kwargs.get("max_tokens"),
                temperature=kwargs.get("temperature"),
                top_p=kwargs.get("top_p"),
            )

            message = response.choices[0].message

            # Перевіряємо, чи OpenAI хоче викликати функцію
            if message.tool_calls:
                # Повертаємо інформацію про виклик функції в форматі, який очікує наша система
                tool_call = message.tool_calls[0]
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    function_args = {}

                # Форматуємо як очікує наш виконавець функцій
                result = f"FUNCTION_CALL:{function_name}:{json.dumps(function_args)}"
                return result
            else:
                # Звичайна текстова відповідь
                return message.content.strip() if message.content else ""

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")


class ModelManager(LoggerMixin):
    """
    Менеджер для управління AI моделями та генерації відповідей.

    Використовує паттерни:
    - Singleton: Забезпечує один екземпляр для всього додатку
    - Strategy: Підтримує різні стратегії генерації (локальні моделі, OpenAI API)

    Функції:
    - Завантаження та управління локальними моделями
    - Робота з OpenAI API
    - Генерація відповідей з підтримкою виклику функцій
    """

    # Змінні класу для реалізації паттерну Singleton
    _instance = None  # Єдиний екземпляр класу
    _model_loaded = False  # Прапор чи завантажена модель

    def __new__(cls) -> "ModelManager":
        """
        Створює новий екземпляр класу або повертає існуючий (Singleton).

        Returns:
            ModelManager: Єдиний екземпляр ModelManager
        """
        if cls._instance is None:
            # Створюємо новий екземпляр тільки якщо його ще немає
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Ініціалізує ModelManager.
        Завантажує модель тільки один раз (через прапор _model_loaded).
        """
        if not self._model_loaded:
            # Ініціалізуємо менеджер конфігурації
            self.config_manager = ConfigurationManager()

            # Змінні для стратегій та моделей
            self.function_calling_strategy: ResponseStrategy
            self.model: Optional[Any] = None
            self.tokenizer: Optional[Any] = None
            self.use_openai: bool = False

            # Перевіряємо, чи треба використовувати OpenAI або локальну модель
            # Читаємо змінну оточення USE_OPENAI
            use_openai = os.getenv("USE_OPENAI", "true").lower() == "true"

            if use_openai:
                # Налаштовуємо OpenAI API
                self._setup_openai()
            else:
                # Завантажуємо локальну модель
                self._load_model()

            # Налаштовуємо стратегії генерації
            self._setup_strategies()
            # Позначаємо, що модель завантажена
            ModelManager._model_loaded = True

    def _setup_openai(self) -> None:
        """
        Налаштовує OpenAI API замість завантаження локальної моделі.

        Встановлює фіктивні значення для model та tokenizer для сумісності,
        оскільки OpenAI API не потребує локальної моделі.
        """
        try:
            # Отримуємо назву моделі OpenAI зі змінної оточення
            openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

            # Створюємо фіктивні атрибути model та tokenizer для сумісності
            # OpenAI API не потребує локальної моделі
            self.model = None
            self.tokenizer = None
            self.use_openai = True

        except Exception as e:
            self.logger.error(f"OpenAI setup error: {str(e)}")
            raise RuntimeError(f"OpenAI setup error: {str(e)}")

    def _load_model(self) -> None:
        """
        Завантажує локальну AI модель та токенізатор.

        Процес завантаження:
        1. Отримання конфігурації моделі
        2. Завантаження моделі через HuggingFace transformers
        3. Завантаження відповідного токенізатора
        4. Перенесення моделі на GPU (якщо доступно)
        """
        try:
            # Отримуємо конфігурацію моделі та системи
            model_config = self.config_manager.model_config
            system_config = self.config_manager.system_config

            # Отримуємо аргументи для завантаження моделі
            model_kwargs = self.config_manager.get_model_kwargs()

            
            # Переносимо модель на відповідний пристрій (GPU) якщо:
            # - не використовуємо accelerate (автоматичне управління пристроями)
            # - пристрій не CPU
            # - модель завантажена успішно
            if (
                not system_config.use_accelerate
                and system_config.device_type != "cpu"
                and self.model is not None
            ):
                self.model = self.model.to(system_config.device_type)

        except Exception as e:
            # Логуємо помилку в журнал для відладки
            self.logger.error(f"Model loading error: {str(e)}")
            # Піднімаємо runtime помилку з більш зрозумілим повідомленням
            raise RuntimeError(f"Model loading error: {str(e)}")

    def _setup_strategies(self) -> None:
        """
        Налаштовує стратегії генерації відповідей.

        Вибирає відповідну стратегію в залежності від типу моделі:
        - OpenAIStrategy для API моделей
        - FunctionCallingStrategy для локальних моделей
        """
        if hasattr(self, "use_openai") and self.use_openai:
            # Налаштовуємо OpenAI стратегії
            openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
            self.function_calling_strategy = OpenAIStrategy(model=openai_model)
        else:
            # Налаштовуємо стратегії для локальних моделей
            self.function_calling_strategy = FunctionCallingStrategy()

    def generate_function_calling_response(self, messages: List[Dict[str, Any]]) -> str:
        """
        Генерує відповідь з можливістю виклику функцій.

        Використовує налаштовану стратегію (OpenAI або локальну модель)
        для генерації відповіді, яка може включати виклики функцій.

        Args:
            messages: Список повідомлень для контексту розмови

        Returns:
            str: Згенерована відповідь або інформація про виклик функції
        """
        try:
            # Отримуємо параметри генерації з конфігурації
            generation_kwargs = self.config_manager.get_generation_kwargs()

            # Викликаємо відповідну стратегію для генерації відповіді
            return self.function_calling_strategy.generate_response(
                self.model,
                self.tokenizer,
                messages,
                generation_kwargs=generation_kwargs,
            )
        except Exception as e:
            self.logger.error(f"Error generating function calling response: {str(e)}")
            return f"Sorry, an error occurred: {str(e)}"

    def prepare_messages(
        self, user_input: str, conversation_history: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Підготовлює повідомлення для введення в модель.

        Створює структуру повідомлень для чату з AI моделлю, включаючи:
        - Системне повідомлення з інструкціями
        - Історію розмови (останні 5 обмінів)
        - Поточний запит користувача

        Args:
            user_input: Поточний запит користувача
            conversation_history: Історія попередніх обмінів (список словників з ключами 'user' та 'assistant')

        Returns:
            List[Dict[str, Any]]: Список повідомлень у форматі для моделі
        """
        # Починаємо з системного повідомлення, яке задає контекст і правила для AI
        messages = [
            {
                "role": "system",
                "content": FunctionDefinitions.SYSTEM_PROMPT,
            }
        ]

        # Додаємо недавню історію розмови (останні 5 обмінів для уникнення переповнення контексту)
        # Обмежуємо історію, щоб не перевищити ліміт токенів моделі
        recent_history = (
            conversation_history[-5:]
            if len(conversation_history) > 5
            else conversation_history
        )
        # Проходимо по кожному обміну в історії та додаємо повідомлення користувача і асистента
        for exchange in recent_history:
            messages.append({"role": "user", "content": exchange["user"]})
            messages.append({"role": "assistant", "content": exchange["assistant"]})

        # Додаємо поточний запит користувача в кінці
        messages.append({"role": "user", "content": user_input})

        return messages  # type: ignore
