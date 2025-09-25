# Code Review: htmladapt

This review evaluates the quality, structure, and maintainability of the `htmladapt` codebase based on the Python source files and associated tests.

## Overall Assessment

The `htmladapt` project is a solid tool for HTML content extraction and merging. It features a clear modular design, good test coverage, and flexible configuration through the `ProcessingConfig` class.

The codebase is generally well-structured but has room for improvement in error handling, documentation consistency, and LLM integration design.

## Strengths

*   **Project Structure:** Clean organization into `core`, `algorithms`, `llm`, and `utils` modules
*   **Configuration Management:** `ProcessingConfig` class with factory methods for different performance profiles
*   **Comprehensive Testing:** Good unit and integration test coverage
*   **Modularity:** Well-encapsulated components like `IDGenerator`, `ElementMatcher`, and `HTMLParser`
*   **Robust Parsing:** Fallback mechanism for different HTML parsing backends
*   **Extensible Architecture:** Design supports future enhancements

## Areas for Improvement

### 1. Inconsistent Docstrings

Documentation format varies across modules. Some use reStructuredText style, others are free-form.

**Recommendation:** Standardize on Google Python Style Guide format for consistent, tool-friendly documentation.

### 2. Generic Exception Handling

Broad `except Exception` blocks in `HTMLExtractMergeTool.extract` and `merge` methods obscure error sources.

**File:** `src/htmladapt/core/extractor_merger.py`

```python
def extract(self, html: str) -> tuple[str, str]:
    ...
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise
```

**Recommendation:** Catch specific exceptions (`ValueError`, `TypeError`, etc.) with more detailed context.

### 3. Tight Coupling in LLMReconciler

The class directly depends on OpenAI API, making it difficult to swap providers or use local models.

**File:** `src/htmladapt/llm/reconciler.py`

**Recommendation:** Create an abstract base class defining a common interface. `OpenAIReconciler` becomes one implementation.

### 4. Missing Type Hint for llm_reconciler

The parameter lacks proper type annotation.

**File:** `src/htmladapt/core/extractor_merger.py`

```python
def __init__(
    self,
    config: ProcessingConfig | None = None,
    llm_reconciler=None  # Optional LLM integration
) -> None:
```

**Recommendation:** Add type hint using the abstract base class from recommendation #3.

```python
from htmladapt.llm.base import BaseReconciler

def __init__(
    self,
    config: ProcessingConfig | None = None,
    llm_reconciler: BaseReconciler | None = None
) -> None:
```

### 5. Hardcoded Weights in ElementMatcher

Similarity calculation uses fixed weights that can't be adjusted by users.

**File:** `src/htmladapt/algorithms/matcher.py`

```python
def _calculate_similarity(self, elem1: Tag, elem2: Tag) -> float:
    ...
    combined_score = (
        id_score * 0.4 +
        hash_score * 0.3 +
        text_score * 0.2 +
        structure_score * 0.1
    )
```

**Recommendation:** Move weights to `ProcessingConfig` to make them user-configurable.

### 6. Redundant HTML Parsing

`original_html` gets parsed into `original_soup` but may not be used in the merging logic.

**Recommendation:** Verify if parsing `original_html` is necessary. Remove if redundant for minor performance gains.

## Actionable Recommendations

1.  **Standardize Docstrings:** Apply consistent Google style format throughout
2.  **Refactor Exception Handling:** Replace broad exception blocks with specific catches
3.  **Abstract LLM Reconciler:** Create `BaseReconciler` interface and update type hints
4.  **Make Matcher Weights Configurable:** Move similarity weights to `ProcessingConfig`
5.  **Review Parser Usage:** Remove unnecessary parsing in `merge` method if confirmed redundant