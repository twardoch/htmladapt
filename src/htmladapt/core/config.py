# this_file: src/htmladapt/core/config.py
"""Configuration classes for HTMLAdapt processing."""

from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class ProcessingConfig:
    """Configuration settings for HTMLAdapt processing.

    This class defines all configurable parameters for HTML extraction,
    matching, and merging operations.

    Attributes:
        id_prefix: Prefix for generated element IDs
        similarity_threshold: Minimum similarity score for fuzzy matching (0.0-1.0)
        enable_llm_resolution: Whether to use LLM for conflict resolution
        llm_model: LLM model name for conflict resolution
        performance_profile: Processing profile affecting speed vs accuracy
        max_context_tokens: Maximum tokens per LLM request
        parser_preference: Preferred HTML parser backend order
        max_depth_limit: Maximum nesting depth for processing
        memory_limit_mb: Maximum memory usage in megabytes
    """

    # ID generation settings
    id_prefix: str = "auto_"

    # Matching algorithm settings
    similarity_threshold: float = 0.7

    # LLM integration settings
    enable_llm_resolution: bool = False
    llm_model: str = "gpt-4o-mini"
    max_context_tokens: int = 1000

    # Performance settings
    performance_profile: Literal["fast", "balanced", "accurate"] = "balanced"
    parser_preference: list[str] = None
    max_depth_limit: int = 100
    memory_limit_mb: int = 512

    def __post_init__(self) -> None:
        """Validate and set default values after initialization."""
        if self.parser_preference is None:
            self.parser_preference = ["lxml", "html5lib", "html.parser"]

        # Validate threshold
        if not 0.0 <= self.similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")

        # Validate max_context_tokens
        if self.max_context_tokens < 100:
            raise ValueError("max_context_tokens must be at least 100")

        # Validate memory limit
        if self.memory_limit_mb < 1:
            raise ValueError("memory_limit_mb must be at least 1")

    @classmethod
    def fast_profile(cls, **kwargs) -> "ProcessingConfig":
        """Create a configuration optimized for speed.

        Returns:
            ProcessingConfig: Configuration with fast processing settings
        """
        defaults = {
            "performance_profile": "fast",
            "similarity_threshold": 0.8,
            "enable_llm_resolution": False,
            "parser_preference": ["lxml", "html.parser"],
        }
        defaults.update(kwargs)
        return cls(**defaults)

    @classmethod
    def accurate_profile(cls, **kwargs) -> "ProcessingConfig":
        """Create a configuration optimized for accuracy.

        Returns:
            ProcessingConfig: Configuration with accurate processing settings
        """
        defaults = {
            "performance_profile": "accurate",
            "similarity_threshold": 0.6,
            "enable_llm_resolution": True,
            "parser_preference": ["html5lib", "lxml", "html.parser"],
        }
        defaults.update(kwargs)
        return cls(**defaults)

    @classmethod
    def balanced_profile(cls, **kwargs) -> "ProcessingConfig":
        """Create a configuration with balanced speed and accuracy.

        Returns:
            ProcessingConfig: Configuration with balanced processing settings
        """
        defaults = {
            "performance_profile": "balanced",
            "similarity_threshold": 0.7,
            "enable_llm_resolution": False,
            "parser_preference": ["lxml", "html5lib", "html.parser"],
        }
        defaults.update(kwargs)
        return cls(**defaults)