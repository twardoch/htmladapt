# this_file: src/htmladapt/__init__.py
"""HTMLAdapt: Intelligent HTML Content Extraction and Merge Tool

HTMLAdapt is a Python-based tool for bidirectional HTML document transformation
that preserves structural integrity while enabling seamless content modification
through an intermediate representation.
"""

from htmladapt.__version__ import __version__
from htmladapt.config import ProcessingConfig
from htmladapt.tool import HTMLExtractMergeTool

__all__ = [
    "HTMLExtractMergeTool",
    "ProcessingConfig",
    "__version__",
]
