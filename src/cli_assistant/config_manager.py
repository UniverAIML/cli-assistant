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
import torch


@dataclass
class ModelConfig:
    """Конфігурація для AI моделі."""

    model_name: str = "Qwen/Qwen2.5-Coder-3B-Instruct"  # Назва моделі з HuggingFace Hub
    max_new_tokens: int = 300  # Максимальна кількість нових токенів для генерації
    temperature: float = (
        0.3  # Параметр креативності (0.0 - детермінований, 1.0 - творчий)
    )
    do_sample: bool = True  # Використовувати sampling замість greedy decoding
    torch_dtype: str = "auto"  # Тип даних PyTorch для моделі
    trust_remote_code: bool = True  # Дозволити виконання коду з репозиторію


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
    torch_dtype: torch.dtype  # Тип даних PyTorch для обчислень
    device_map: Optional[str]  # Мапа пристроїв для розподілу моделі
    use_accelerate: bool  # Чи використовувати бібліотеку accelerate
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
            self._detect_system_config()  # Виявляємо системні можливості
            self._setup_model_config()  # Налаштовуємо модель
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

    def _detect_system_config(self) -> None:
        """Виявляє оптимальну системну конфігурацію для завантаження моделі."""
        system_platform = platform.system().lower()
        cuda_available = torch.cuda.is_available()
        # Перевіряємо наявність Apple Silicon MPS
        mps_available = (
            torch.backends.mps.is_available()
            if hasattr(torch.backends, "mps")
            else False
        )

        # Визначаємо оптимальну конфігурацію пристрою
        if system_platform == "darwin" and mps_available:
            # macOS з Apple Silicon (M1/M2/M3)
            device_type = "mps"
            torch_dtype = torch.float16  # Половинна точність для економії пам'яті
            device_map = None  # MPS не підтримує device_map
            use_accelerate = False  # Не потрібно для MPS
            device_info = f"Platform: macOS, MPS available: {mps_available}"
        elif cuda_available and system_platform in ["windows", "linux"]:
            # Windows/Linux з NVIDIA GPU
            device_type = "cuda"
            torch_dtype = torch.float16  # Половинна точність для GPU
            device_map = "auto"  # Автоматичне розподілення по GPU
            use_accelerate = True  # Використовуємо accelerate для оптимізації
            device_info = f"Platform: {system_platform}, CUDA available: {cuda_available}, GPU count: {torch.cuda.device_count()}, Current device: {torch.cuda.get_device_name()}"
        else:
            # Резервний варіант CPU для будь-якої платформи
            device_type = "cpu"
            torch_dtype = torch.float32  # Повна точність для CPU
            device_map = None  # CPU не потребує device_map
            use_accelerate = False  # Не потрібно для CPU
            device_info = f"Platform: {system_platform}, Using CPU mode"

        # Створюємо конфігурацію системи
        self.system_config = SystemConfig(
            platform=system_platform,
            device_type=device_type,
            torch_dtype=torch_dtype,
            device_map=device_map,
            use_accelerate=use_accelerate,
            device_info=device_info,
        )

    def _setup_model_config(self) -> None:
        """Налаштовує конфігурацію моделі."""
        self.model_config = ModelConfig()

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

    def get_model_kwargs(self) -> Dict[str, Any]:
        """Отримує аргументи для завантаження моделі на основі системної конфігурації."""
        model_kwargs = {
            "torch_dtype": self.model_config.torch_dtype,
            "trust_remote_code": self.model_config.trust_remote_code,
        }

        # Додаємо device_map тільки якщо використовуємо accelerate
        if self.system_config.use_accelerate:
            model_kwargs["device_map"] = self.system_config.device_map

        return model_kwargs

    def get_generation_kwargs(self) -> Dict[str, Any]:
        """Отримує аргументи для генерації тексту."""
        return {
            "max_new_tokens": self.model_config.max_new_tokens,
            "temperature": self.model_config.temperature,
            "do_sample": self.model_config.do_sample,
        }

    def get_openai_kwargs(self) -> Dict[str, Any]:
        """Отримує аргументи для OpenAI API."""
        return {
            "model": self.openai_config.model_name,
            "max_tokens": self.openai_config.max_tokens,
            "temperature": self.openai_config.temperature,
            "top_p": self.openai_config.top_p,
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
