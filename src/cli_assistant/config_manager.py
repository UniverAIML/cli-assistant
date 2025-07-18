"""Configuration and logging management for the CLI Assistant."""

import logging
import os
import platform
from dataclasses import dataclass
from typing import Optional, Dict, Any
import torch


@dataclass
class ModelConfig:
    """Configuration for the AI model."""

    model_name: str = "Qwen/Qwen2.5-Coder-3B-Instruct"
    max_new_tokens: int = 300
    temperature: float = 0.3
    do_sample: bool = True
    torch_dtype: str = "auto"
    trust_remote_code: bool = True


@dataclass
class OpenAIConfig:
    """Configuration for OpenAI API."""

    api_key: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 1.0
    timeout: int = 30


@dataclass
class ProviderConfig:
    """Configuration for AI provider selection."""

    provider: str = "local"  # "local" or "openai"
    use_openai: bool = False


@dataclass
class SystemConfig:
    """System configuration for device detection and optimization."""

    platform: str
    device_type: str
    torch_dtype: torch.dtype
    device_map: Optional[str]
    use_accelerate: bool
    device_info: str


class ConfigurationManager:
    """Manages configuration for the CLI Assistant using Singleton pattern."""

    _instance = None
    _initialized = False

    def __new__(cls) -> "ConfigurationManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._setup_logging()
            self._setup_provider_config()
            self._detect_system_config()
            self._setup_model_config()
            self._setup_openai_config()
            ConfigurationManager._initialized = True

    def _setup_logging(self) -> None:
        """Configure logging for the application."""
        # Disable transformers warnings and progress bars
        logging.getLogger("transformers").setLevel(logging.ERROR)
        logging.getLogger("accelerate").setLevel(logging.ERROR)
        os.environ["TRANSFORMERS_VERBOSITY"] = "error"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

        # Enable detailed HTTP request logs from OpenAI and httpx for debugging
        logging.getLogger("httpx").setLevel(logging.ERROR)
        logging.getLogger("openai").setLevel(logging.ERROR)
        logging.getLogger("openai._base_client").setLevel(logging.ERROR)

        # Disable tqdm progress bars globally
        try:
            from tqdm import tqdm  # type: ignore[import-untyped]

            tqdm.disable = True
        except ImportError:
            pass

        # Setup application logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def _setup_provider_config(self) -> None:
        """Setup AI provider configuration based on environment variables."""
        use_openai = os.getenv("USE_OPENAI", "false").lower() == "true"
        provider = "openai" if use_openai else "local"

        self.provider_config = ProviderConfig(provider=provider, use_openai=use_openai)

        self.logger.info(f"AI Provider: {provider}")

    def _detect_system_config(self) -> None:
        """Detect optimal system configuration for model loading."""
        system_platform = platform.system().lower()
        cuda_available = torch.cuda.is_available()
        mps_available = (
            torch.backends.mps.is_available()
            if hasattr(torch.backends, "mps")
            else False
        )

        # Determine optimal device configuration
        if system_platform == "darwin" and mps_available:
            # macOS with Apple Silicon
            device_type = "mps"
            torch_dtype = torch.float16
            device_map = None
            use_accelerate = False
            device_info = f"Platform: macOS, MPS available: {mps_available}"
        elif cuda_available and system_platform in ["windows", "linux"]:
            # Windows/Linux with NVIDIA GPU
            device_type = "cuda"
            torch_dtype = torch.float16
            device_map = "auto"
            use_accelerate = True
            device_info = f"Platform: {system_platform}, CUDA available: {cuda_available}, GPU count: {torch.cuda.device_count()}, Current device: {torch.cuda.get_device_name()}"
        else:
            # CPU fallback for any platform
            device_type = "cpu"
            torch_dtype = torch.float32
            device_map = None
            use_accelerate = False
            device_info = f"Platform: {system_platform}, Using CPU mode"

        self.system_config = SystemConfig(
            platform=system_platform,
            device_type=device_type,
            torch_dtype=torch_dtype,
            device_map=device_map,
            use_accelerate=use_accelerate,
            device_info=device_info,
        )

        self.logger.info(f"Detected system configuration: {device_info}")

    def _setup_model_config(self) -> None:
        """Setup model configuration."""
        self.model_config = ModelConfig()

    def _setup_openai_config(self) -> None:
        """Setup OpenAI configuration based on environment variables."""
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

        if self.provider_config.use_openai:
            if not api_key:
                self.logger.warning(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
                )
            else:
                self.logger.info(f"OpenAI model configured: {model_name}")

    def get_model_kwargs(self) -> Dict[str, Any]:
        """Get model loading arguments based on system configuration."""
        model_kwargs = {
            "torch_dtype": self.model_config.torch_dtype,
            "trust_remote_code": self.model_config.trust_remote_code,
        }

        if self.system_config.use_accelerate:
            model_kwargs["device_map"] = self.system_config.device_map

        return model_kwargs

    def get_generation_kwargs(self) -> Dict[str, Any]:
        """Get text generation arguments."""
        return {
            "max_new_tokens": self.model_config.max_new_tokens,
            "temperature": self.model_config.temperature,
            "do_sample": self.model_config.do_sample,
        }

    def get_openai_kwargs(self) -> Dict[str, Any]:
        """Get OpenAI API arguments."""
        return {
            "model": self.openai_config.model_name,
            "max_tokens": self.openai_config.max_tokens,
            "temperature": self.openai_config.temperature,
            "top_p": self.openai_config.top_p,
        }

    def is_openai_enabled(self) -> bool:
        """Check if OpenAI provider is enabled and configured."""
        return (
            self.provider_config.use_openai and self.openai_config.api_key is not None
        )

    def get_provider_type(self) -> str:
        """Get the current AI provider type."""
        return self.provider_config.provider


class LoggerMixin:
    """Mixin class to provide logging capabilities to other classes."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for the current class."""
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
