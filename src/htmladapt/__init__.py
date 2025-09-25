# this_file: src/htmladapt/__init__.py
"""HTMLAdapt: Intelligent HTML Content Extraction and Merge Tool

HTMLAdapt is a Python-based tool for bidirectional HTML document transformation
that preserves structural integrity while enabling seamless content modification
through an intermediate representation.
"""

from htmladapt.__version__ import __version__

from htmladapt.core.config import ProcessingConfig
from htmladapt.core.extractor_merger import HTMLExtractMergeTool
from htmladapt.llm.reconciler import LLMReconciler

__all__ = [
    "__version__",
    "HTMLExtractMergeTool",
    "ProcessingConfig",
    "LLMReconciler",
]