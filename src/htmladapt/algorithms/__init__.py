# this_file: src/htmladapt/algorithms/__init__.py
"""Algorithm modules for HTMLAdapt processing."""

from htmladapt.algorithms.id_generation import IDGenerator
from htmladapt.algorithms.matcher import ElementMatcher

__all__ = [
    "IDGenerator",
    "ElementMatcher",
]