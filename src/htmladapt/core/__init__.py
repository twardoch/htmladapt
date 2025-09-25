# this_file: src/htmladapt/core/__init__.py
"""Core modules for HTMLAdapt functionality."""

from htmladapt.core.config import ProcessingConfig
from htmladapt.core.extractor_merger import HTMLExtractMergeTool

__all__ = [
    "ProcessingConfig",
    "HTMLExtractMergeTool",
]