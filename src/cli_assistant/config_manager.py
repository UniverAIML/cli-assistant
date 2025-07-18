"""
Управління конфігурацією та логуванням для CLI Assistant.
Цей модуль містить класи для налаштування різних аспектів додатку:
- Конфігурація AI моделей
- Налаштування OpenAI API
- Визначення системних параметрів
- Управління логуванням
"""

import logging
import os
import platform
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class OpenAIConfig:
    """Конфігурація для OpenAI API."""

    api_key: Optional[str] = None  # API ключ для OpenAI
    model_name: str = "gpt-3.5-turbo"  # Назва моделі OpenAI
    max_tokens: int = 1000  # Максимальна кількість токенів у відповіді
    temperature: float = 0.7  # Параметр креативності
    top_p: float = 1.0  # Параметр nucleus sampling
    timeout: int = 30  # Таймаут для API запитів (секунди)


@dataclass
class ProviderConfig:
    """Конфігурація для вибору AI провайдера."""

    provider: str = "local"  # Тип провайдера: "local" або "openai"
    use_openai: bool = False  # Чи використовувати OpenAI замість локальної моделі


@dataclass
class SystemConfig:
    """Системна конфігурація для виявлення пристроїв та оптимізації."""

    platform: str  # Операційна система (windows, linux, darwin)
    device_type: str  # Тип пристрою (cpu, cuda, mps)
    device_map: Optional[str]  # Мапа пристроїв для розподілу моделі
    device_info: str  # Детальна інформація про пристрій


class ConfigurationManager:
    """
    Управляє конфігурацією для CLI Assistant використовуючи паттерн Singleton.

    Цей клас забезпечує єдину точку доступу до всіх налаштувань додатку:
    - Автоматичне виявлення системних можливостей
    - Налаштування логування
    - Конфігурація AI моделей та провайдерів
    - Оптимізація під конкретне залізо
    """

    # Змінні класу для реалізації Singleton патерну
    _instance = None  # Єдиний екземпляр класу
    _initialized = False  # Прапор ініціалізації

    def __new__(cls) -> "ConfigurationManager":
        """Створює новий екземпляр або повертає існуючий (Singleton)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Ініціалізує ConfigurationManager тільки один раз."""
        if not self._initialized:
            # Послідовність ініціалізації важлива
            self._setup_logging()  # Спочатку налаштовуємо логування
            self._setup_provider_config()  # Потім провайдер AI
            self._setup_openai_config()  # Налаштовуємо OpenAI
            ConfigurationManager._initialized = True

    def _setup_logging(self) -> None:
        """Налаштовує логування для додатку."""
        # Відключаємо зайві повідомлення від transformers та accelerate
        logging.getLogger("transformers").setLevel(logging.ERROR)
        logging.getLogger("accelerate").setLevel(logging.ERROR)
        os.environ["TRANSFORMERS_VERBOSITY"] = "error"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

        # Відключаємо детальні HTTP логи від OpenAI та httpx для чистішого виводу
        logging.getLogger("httpx").setLevel(logging.ERROR)
        logging.getLogger("openai").setLevel(logging.ERROR)
        logging.getLogger("openai._base_client").setLevel(logging.ERROR)

        # Відключаємо progress bar від tqdm глобально
        try:
            from tqdm import tqdm  # type: ignore[import-untyped]

            tqdm.disable = True
        except ImportError:
            pass

        # Налаштовуємо базове логування додатку
        logging.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def _setup_provider_config(self) -> None:
        """Налаштовує конфігурацію AI провайдера на основі змінних оточення."""
        # Читаємо змінну оточення USE_OPENAI
        use_openai = os.getenv("USE_OPENAI", "true").lower() == "true"
        provider = "openai" if use_openai else "local"

        self.provider_config = ProviderConfig(provider=provider, use_openai=use_openai)

    def _setup_openai_config(self) -> None:
        """Налаштовує конфігурацію OpenAI на основі змінних оточення."""
        # Читаємо налаштування з змінних оточення
        api_key = os.getenv("OPENAI_API_KEY")
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        self.openai_config = OpenAIConfig(
            api_key=api_key,
            model_name=model_name,
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            top_p=float(os.getenv("OPENAI_TOP_P", "1.0")),
            timeout=int(os.getenv("OPENAI_TIMEOUT", "30")),
        )

        # Перевіряємо наявність API ключа якщо використовуємо OpenAI
        if self.provider_config.use_openai:
            if not api_key:
                self.logger.warning(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
                )
            else:
                pass

    
    def get_openai_kwargs(self) -> Dict[str, Any]:
        """Отримує аргументи для OpenAI API."""
        return {
            "model": self.openai_config.model_name,
            "max_tokens": self.openai_config.max_tokens,
            "temperature": self.openai_config.temperature,
            "top_p": self.openai_config.top_p,
        }

    def get_generation_kwargs(self) -> Dict[str, Any]:
        """Отримує параметри генерації для локальних моделей."""
        return {
            "max_new_tokens": self.openai_config.max_tokens,
            "temperature": self.openai_config.temperature,
            "top_p": self.openai_config.top_p,
            "do_sample": True,
            "pad_token_id": None,  # Буде встановлено в generate_local_response
        }

    def is_openai_enabled(self) -> bool:
        """Перевіряє чи включений та налаштований OpenAI провайдер."""
        return (
            self.provider_config.use_openai and self.openai_config.api_key is not None
        )

    def get_provider_type(self) -> str:
        """Отримує тип поточного AI провайдера."""
        return self.provider_config.provider


class LoggerMixin:
    """Mixin клас для надання можливостей логування іншим класам."""

    @property
    def logger(self) -> logging.Logger:
        """Отримує logger для поточного класу."""
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
