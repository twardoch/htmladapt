# this_file: tests/test_config.py
"""Tests for ProcessingConfig class."""

import pytest
from htmladapt.core.config import ProcessingConfig


class TestProcessingConfig:
    """Test ProcessingConfig functionality."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ProcessingConfig()

        assert config.id_prefix == "auto_"
        assert config.similarity_threshold == 0.7
        assert config.enable_llm_resolution is False
        assert config.performance_profile == "balanced"
        assert config.parser_preference == ["lxml", "html5lib", "html.parser"]

    def test_custom_config(self):
        """Test custom configuration values."""
        config = ProcessingConfig(
            id_prefix="test_",
            similarity_threshold=0.8,
            enable_llm_resolution=True,
            performance_profile="accurate"
        )

        assert config.id_prefix == "test_"
        assert config.similarity_threshold == 0.8
        assert config.enable_llm_resolution is True
        assert config.performance_profile == "accurate"

    def test_similarity_threshold_validation(self):
        """Test similarity threshold validation."""
        # Valid thresholds
        ProcessingConfig(similarity_threshold=0.0)
        ProcessingConfig(similarity_threshold=1.0)
        ProcessingConfig(similarity_threshold=0.5)

        # Invalid thresholds
        with pytest.raises(ValueError, match="similarity_threshold must be between 0.0 and 1.0"):
            ProcessingConfig(similarity_threshold=-0.1)

        with pytest.raises(ValueError, match="similarity_threshold must be between 0.0 and 1.0"):
            ProcessingConfig(similarity_threshold=1.1)

    def test_max_context_tokens_validation(self):
        """Test max context tokens validation."""
        # Valid values
        ProcessingConfig(max_context_tokens=100)
        ProcessingConfig(max_context_tokens=5000)

        # Invalid values
        with pytest.raises(ValueError, match="max_context_tokens must be at least 100"):
            ProcessingConfig(max_context_tokens=50)

    def test_memory_limit_validation(self):
        """Test memory limit validation."""
        # Valid values
        ProcessingConfig(memory_limit_mb=1)
        ProcessingConfig(memory_limit_mb=1024)

        # Invalid values
        with pytest.raises(ValueError, match="memory_limit_mb must be at least 1"):
            ProcessingConfig(memory_limit_mb=0)

    def test_fast_profile(self):
        """Test fast profile creation."""
        config = ProcessingConfig.fast_profile()

        assert config.performance_profile == "fast"
        assert config.similarity_threshold == 0.8
        assert config.enable_llm_resolution is False
        assert config.parser_preference == ["lxml", "html.parser"]

    def test_accurate_profile(self):
        """Test accurate profile creation."""
        config = ProcessingConfig.accurate_profile()

        assert config.performance_profile == "accurate"
        assert config.similarity_threshold == 0.6
        assert config.enable_llm_resolution is True
        assert config.parser_preference == ["html5lib", "lxml", "html.parser"]

    def test_balanced_profile(self):
        """Test balanced profile creation."""
        config = ProcessingConfig.balanced_profile()

        assert config.performance_profile == "balanced"
        assert config.similarity_threshold == 0.7
        assert config.enable_llm_resolution is False
        assert config.parser_preference == ["lxml", "html5lib", "html.parser"]

    def test_profile_with_overrides(self):
        """Test profile creation with custom overrides."""
        config = ProcessingConfig.fast_profile(
            id_prefix="custom_",
            similarity_threshold=0.9
        )

        assert config.performance_profile == "fast"
        assert config.id_prefix == "custom_"
        assert config.similarity_threshold == 0.9
        assert config.enable_llm_resolution is False