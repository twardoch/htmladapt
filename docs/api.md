---
layout: default
title: API Reference
nav_order: 3
---

# API Reference

### Core Classes

#### `HTMLExtractMergeTool`
Main interface for extraction and merging operations.

Methods:
- `extract(html: str) -> Tuple[str, str]`: Create superset and subset
- `merge(edited: str, subset: str, superset: str, original: str) -> str`: Merge content

#### `ProcessingConfig`
Configuration object for customizing behavior.

Parameters:
- `id_prefix: str`: Prefix for generated IDs (default: "xhq")
- `simi_level: float`: Minimum similarity for fuzzy matching (default: 0.7)
- `llm_use: bool`: Use LLM for conflicts (default: False)
- `perf: str`: Processing profile - fast|balanced|accurate (default: "balanced")

#### `LLMReconciler`
Interface for LLM-powered conflict resolution.

Parameters:
- `api_key: str`: OpenAI API key
- `model: str`: Model name (default: "gpt-4o-mini")
- `max_context_tokens: int`: Maximum tokens per request (default: 1000)

### Utility Functions

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
optimized_html = optimize_for_size(html_content, target_size_mb=5)
```
