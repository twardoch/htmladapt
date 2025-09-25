# this_file: src/htmladapt/htmladapt.py
"""HTMLAdapt: Legacy module for backwards compatibility.

This module provides backwards compatibility imports.
The main implementation is now in htmladapt.core modules.
"""

# Import main classes for backwards compatibility
from htmladapt.core.config import ProcessingConfig
from htmladapt.core.extractor_merger import HTMLExtractMergeTool
from htmladapt.llm.reconciler import LLMReconciler
from htmladapt.utils.helpers import validate_html, estimate_processing_time, optimize_for_size

# Legacy alias for backwards compatibility
Config = ProcessingConfig

__all__ = [
    "HTMLExtractMergeTool",
    "ProcessingConfig",
    "LLMReconciler",
    "validate_html",
    "estimate_processing_time",
    "optimize_for_size",
    # Legacy compatibility
    "Config",
] 