# this_file: tests/test_config.py
"""Tests for ProcessingConfig class."""

import pytest

from htmladapt.config import ProcessingConfig


class TestProcessingConfig:
    """Test ProcessingConfig functionality."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ProcessingConfig()

        assert config.id_prefix == "xhq"
        assert config.simi_level == 0.7

    def test_custom_config(self):
        """Test custom configuration values."""
        config = ProcessingConfig(
            id_prefix="test_",
            simi_level=0.8,
        )

        assert config.id_prefix == "test_"
        assert config.simi_level == 0.8

    def test_simi_level_validation(self):
        """Test similarity threshold validation."""
        # Valid thresholds
        ProcessingConfig(simi_level=0.0)
        ProcessingConfig(simi_level=1.0)
        ProcessingConfig(simi_level=0.5)

        # Invalid thresholds
        with pytest.raises(ValueError, match="simi_level must be between 0.0 and 1.0"):
            ProcessingConfig(simi_level=-0.1)

        with pytest.raises(ValueError, match="simi_level must be between 0.0 and 1.0"):
            ProcessingConfig(simi_level=1.1)
