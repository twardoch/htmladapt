---
layout: default
title: API Reference
nav_order: 3
---

# API Reference

## Core Classes

### `HTMLExtractMergeTool`
Main interface for extraction and merging operations.

**Methods:**
- `extract(html: str) -> Tuple[str, str]`: Returns (superset, subset) pair
- `merge(edited: str, subset: str, superset: str, original: str) -> str`: Merges changes back into original

### `ProcessingConfig`
Configuration for processing behavior.

**Parameters:**
- `id_prefix: str`: Generated ID prefix (default: "xhq")
- `simi_level: float`: Minimum similarity for fuzzy matching (default: 0.7)
- `llm_use: bool`: Enable LLM conflict resolution (default: False)
- `perf: str`: Processing profile - fast|balanced|accurate (default: "balanced")

### `LLMReconciler`
LLM-powered conflict resolution interface.

**Parameters:**
- `api_key: str`: OpenAI API key
- `model: str`: Model name (default: "gpt-4o-mini")
- `max_context_tokens: int`: Maximum tokens per request (default: 1000)

## Utility Functions

```python
from htmladapt.utils import (
    validate_html,
    estimate_processing_time,
    optimize_for_size
)

# Validate HTML before processing
is_valid, issues = validate_html(html_content)

# Estimate processing requirements
time_estimate, memory_estimate = estimate_processing_time(html_content)

# Optimize large documents
optimized_html = optimize_for_size(html_content, target_size_mb