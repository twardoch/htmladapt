# this_file: src/htmladapt/utils/__init__.py
"""Utility modules for HTMLAdapt."""

from htmladapt.utils.helpers import validate_html, estimate_processing_time, optimize_for_size

__all__ = [
    "validate_html",
    "estimate_processing_time",
    "optimize_for_size",
]