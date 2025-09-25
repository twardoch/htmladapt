# this_file: tests/test_id_generation.py
"""Tests for IDGenerator class."""

import pytest
from htmladapt.algorithms.id_generation import IDGenerator


class TestIDGenerator:
    """Test IDGenerator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = IDGenerator()

    def test_basic_id_generation(self):
        """Test basic ID generation."""
        id1 = self.generator.generate_id()
        id2 = self.generator.generate_id()

        assert id1.startswith("auto_")
        assert id2.startswith("auto_")
        assert id1 != id2

    def test_custom_prefix(self):
        """Test ID generation with custom prefix."""
        generator = IDGenerator(prefix="test_")
        generated_id = generator.generate_id()

        assert generated_id.startswith("test_")

    def test_element_hint(self):
        """Test ID generation with element hint."""
        generated_id = self.generator.generate_id(element_hint="p")

        assert "p_" in generated_id

    def test_collision_detection(self):
        """Test collision detection and avoidance."""
        # Generate some IDs
        ids = [self.generator.generate_id() for _ in range(100)]

        # All IDs should be unique
        assert len(ids) == len(set(ids))

    def test_register_existing_id(self):
        """Test registering existing IDs."""
        existing_id = "existing_id"
        self.generator.register_existing_id(existing_id)

        # Generate many IDs and make sure the existing one is not used
        generated_ids = [self.generator.generate_id() for _ in range(50)]
        assert existing_id not in generated_ids

    def test_is_generated_id(self):
        """Test checking if ID was generated."""
        generated_id = self.generator.generate_id()
        external_id = "external_id"

        assert self.generator.is_generated_id(generated_id) is True
        assert self.generator.is_generated_id(external_id) is False

    def test_reset(self):
        """Test generator reset functionality."""
        # Generate some IDs
        self.generator.generate_id()
        self.generator.generate_id()
        self.generator.register_existing_id("test_id")

        # Reset and check state
        self.generator.reset()
        stats = self.generator.stats

        assert stats["counter"] == 0
        assert stats["used_ids_count"] == 0

    def test_base36_conversion(self):
        """Test base36 conversion."""
        assert self.generator._to_base36(0) == "0"
        assert self.generator._to_base36(1) == "1"
        assert self.generator._to_base36(35) == "z"
        assert self.generator._to_base36(36) == "10"
        assert self.generator._to_base36(1295) == "zz"

    def test_stats(self):
        """Test generator statistics."""
        # Initial stats
        stats = self.generator.stats
        assert stats["counter"] == 0
        assert stats["used_ids_count"] == 0

        # Generate some IDs
        self.generator.generate_id()
        self.generator.generate_id()
        self.generator.register_existing_id("external")

        stats = self.generator.stats
        assert stats["counter"] == 2
        assert stats["used_ids_count"] == 3  # 2 generated + 1 registered

    def test_id_uniqueness_stress(self):
        """Test ID uniqueness under stress."""
        num_ids = 1000
        ids = set()

        for _ in range(num_ids):
            generated_id = self.generator.generate_id()
            assert generated_id not in ids
            ids.add(generated_id)

        assert len(ids) == num_ids