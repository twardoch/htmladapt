
---
title: API Reference
layout: default
nav_order: 3
parent: Home
---

# API Reference

This document provides a reference for the core classes and functions in the `htmladapt` package.

## Core Classes

### `HTMLExtractMergeTool`

The main interface for all extraction and merging operations.

```python
class HTMLExtractMergeTool:
    def __init__(self, config: ProcessingConfig = None, llm_reconciler: LLMReconciler = None):
        # ...
```

**Methods:**

- `extract(html: str) -> Tuple[str, str]`
  :   Takes a string of original HTML and returns a tuple containing the `superset_html` and `subset_html`.

- `merge(edited: str, subset: str, superset: str, original: str) -> str`
  :   Performs the three-way merge. It takes the `edited` subset, the original `subset`, the `superset`, and the `original` HTML to produce the final, merged HTML string.

---

### `ProcessingConfig`

A Pydantic model for customizing the tool's behavior.

```python
class ProcessingConfig(BaseModel):
    id_prefix: str = "auto_"
    similarity_threshold: float = 0.7
    enable_llm_resolution: bool = False
    llm_model: str = "gpt-4o-mini"
    performance_profile: str = "balanced"
```

**Parameters:**

- `id_prefix` (str): A string prefix for the unique IDs generated during the extraction phase. Default: `"auto_"`.
- `similarity_threshold` (float): The minimum similarity score (0.0 to 1.0) for fuzzy matching. Default: `0.7`.
- `enable_llm_resolution` (bool): If `True`, enables the use of an LLM for resolving complex conflicts. Default: `False`.
- `llm_model` (str): The model name to use for LLM-based resolution. Default: `"gpt-4o-mini"`.
- `performance_profile` (str): The performance profile to use. Options are `"fast"`, `"balanced"`, or `"accurate"`. Default: `"balanced"`.

---

### `LLMReconciler`

An interface for providing LLM-powered conflict resolution.

```python
class LLMReconciler:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", max_context_tokens: int = 1000):
        # ...
```

**Parameters:**

- `api_key` (str): Your API key for the LLM provider (e.g., OpenAI).
- `model` (str): The specific model to use for reconciliation. Default: `"gpt-4o-mini"`.
- `max_context_tokens` (int): The maximum number of tokens to include in each request to the LLM. Default: `1000`.

## Utility Functions

`htmladapt` also provides several utility functions for advanced use cases.

```python
from htmladapt.utils import (
    validate_html,
    estimate_processing_time,
    optimize_for_size
)

# Validate HTML syntax before processing
is_valid, issues = validate_html(html_content)

# Get a rough estimate of processing time and memory usage
time_estimate, memory_estimate = estimate_processing_time(html_content)

# Pre-process very large documents to optimize them for size
optimized_html = optimize_for_size(html_content, target_size_mb=5)
```
