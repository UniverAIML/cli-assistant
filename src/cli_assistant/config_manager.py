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
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            self._detect_system_config()
            self._setup_model_config()
            ConfigurationManager._initialized = True
    
    def _setup_logging(self) -> None:
        """Configure logging for the application."""
        # Disable transformers warnings and progress bars
        logging.getLogger("transformers").setLevel(logging.ERROR)
        logging.getLogger("accelerate").setLevel(logging.ERROR)
        os.environ["TRANSFORMERS_VERBOSITY"] = "error"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        # Disable tqdm progress bars globally
        try:
            from tqdm import tqdm
            tqdm.disable = True
        except ImportError:
            pass
        
        # Setup application logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
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
            device_info=device_info
        )
        
        self.logger.info(f"Detected system configuration: {device_info}")
    
    def _setup_model_config(self) -> None:
        """Setup model configuration."""
        self.model_config = ModelConfig()
    
    def get_model_kwargs(self) -> Dict[str, Any]:
        """Get model loading arguments based on system configuration."""
        model_kwargs = {
            "torch_dtype": self.model_config.torch_dtype,
            "trust_remote_code": self.model_config.trust_remote_code
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


class LoggerMixin:
    """Mixin class to provide logging capabilities to other classes."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for the current class."""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
