# this_file: src/htmladapt/config.py
"""Configuration classes for HTMLAdapt processing."""

from dataclasses import dataclass


@dataclass
class ProcessingConfig:
    """Configuration settings for HTMLAdapt processing.

    This class defines configurable parameters for HTML extraction,
    matching, and merging operations.

    Attributes:
        id_prefix: Prefix for generated element IDs
        simi_level: Minimum similarity score for fuzzy matching (0.0-1.0)
    """

    # ID generation settings
    id_prefix: str = "xhq"

    # Matching algorithm settings
    simi_level: float = 0.7

    def __post_init__(self) -> None:
        """Validate configuration values."""
        # Validate threshold
        if not 0.0 <= self.simi_level <= 1.0:
            msg = "simi_level must be between 0.0 and 1.0"
            raise ValueError(msg)
