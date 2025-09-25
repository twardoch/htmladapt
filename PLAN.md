# Refactoring and Simplification Plan

This plan outlines the steps to refactor the `htmladapt` codebase to be leaner, flatter, and more focused on its core functionality.

## 1. Core Objective

The primary goal of `htmladapt` is to provide a robust tool for extracting content from an HTML document into a separate file for editing (e.g., translation) and then merging the edited content back into the original HTML structure, preserving all formatting, styles, and scripts.

## 2. Simplification and Feature Removal

To align with the "Simple Tool" philosophy, the following features and components will be removed or simplified. The focus is on removing "enterprise" features that are not essential for the core use case.

### 2.1. Remove LLM-based Reconciliation
The `src/htmladapt/llm` module, including the `LLMReconciler`, will be removed.
-   **Reasoning:** LLM-based reconciliation adds significant complexity (API keys, external dependencies, prompts) and is not part of the core deterministic functionality. The tool should focus on robust algorithmic matching. Fuzzy matching should be the fallback for non-perfect matches.
-   **Action:**
    -   Delete the `src/htmladapt/llm` directory.
    -   Remove any related code in `extractor_merger.py` that calls the `LLMReconciler`.
    -   Remove `llm_use` and `model_llm` from `ProcessingConfig` in `src/htmladapt/core/config.py`.
    -   Remove LLM-related options from the CLI in `src/htmladapt/__main__.py`.

### 2.2. Remove Utility Functions
The `src/htmladapt/utils` directory and its contents will be removed.
-   **Reasoning:** Functions like `validate_html`, `estimate_processing_time`, and `optimize_for_size` are auxiliary and add bloat. The library should assume valid HTML as input and not concern itself with pre-processing or performance estimation.
-   **Action:**
    -   Delete the `src/htmladapt/utils` directory.
    -   Remove any imports and calls to these utility functions from other files (e.g., `htmladapt.py`, `extractor_merger.py`).

### 2.3. Simplify Configuration
The `ProcessingConfig` in `src/htmladapt/core/config.py` will be simplified.
-   **Reasoning:** The `perf` profile ('fast', 'balanced', 'accurate') and its corresponding class methods are an unnecessary abstraction. The configuration should be minimal. The validation and memory/depth limits are also over-engineering for a simple tool.
-   **Action:**
    -   Remove the `perf`, `max_context_tokens`, `parser_preference`, `max_depth_limit`, and `memory_limit_mb` parameters from `ProcessingConfig`.
    -   Remove the `fast_profile`, `accurate_profile`, and `balanced_profile` class methods.
    -   Remove the `__post_init__` validation logic.
    -   The simplified `ProcessingConfig` will only contain `id_prefix` and `simi_level`.
    -   Consider moving these two parameters directly to the `HTMLExtractMergeTool` constructor and removing the `ProcessingConfig` class altogether.

### 2.4. Simplify Parser
The `HTMLParser` in `src/htmladapt/core/parser.py` will be simplified.
- **Reasoning:** The `validate_html` method and parser availability checks are not core to the parsing functionality.
- **Action:**
    - Remove the `validate_html`, `get_parser_info` methods.
    - Simplify the parser selection logic. It should try a list of preferred parsers and fall back gracefully. The current implementation is mostly fine, but can be slightly cleaned up.

### 2.5. Simplify Matcher
The `ElementMatcher` in `src/htmladapt/algorithms/matcher.py` can be simplified.
- **Reasoning:** The weighted combination of multiple similarity scores is complex. A simpler, more direct approach is preferred.
- **Action:**
    - Refactor `_calculate_similarity` to use a simpler priority:
        1. Perfect ID match (score 1.0).
        2. Hash-based content match (score 0.95).
        3. Fuzzy text similarity (score between 0.0 and 1.0).
    - Remove the structural similarity check (`_structure_similarity`) as it adds complexity for little gain in the core use case.

## 3. Code Restructuring and Flattening

The codebase will be restructured to be flatter and more modular.

### 3.1. Flatten the `src/htmladapt` directory
-   **Reasoning:** The separation into `core` and `algorithms` is artificial for a small project. A flat structure is easier to navigate.
-   **Action:**
    -   Move `config.py`, `extractor_merger.py`, `parser.py` from `src/htmladapt/core` to `src/htmladapt`.
    -   Move `id_generation.py`, `matcher.py` from `src/htmladapt/algorithms` to `src/htmladapt`.
    -   Delete the `src/htmladapt/core` and `src/htmladapt/algorithms` directories.
    -   Rename `src/htmladapt/extractor_merger.py` to `src/htmladapt/tool.py`.
    -   Update all imports to reflect the new structure.

### 3.2. Consolidate Entry Point
- **Reasoning:** The `src/htmladapt/htmladapt.py` file is just a facade for imports. This is unnecessary.
- **Action:**
    - Delete `src/htmladapt/htmladapt.py`.
    - Expose the main classes (`HTMLExtractMergeTool`, `ProcessingConfig`) directly from `src/htmladapt/__init__.py`.

The new structure will be:
```
src/htmladapt/
├── __init__.py
├── __main__.py
├── tool.py           # (was extractor_merger.py)
├── config.py
├── parser.py
├── id_generation.py
└── matcher.py
```

## 4. CLI Simplification

- **Reasoning:** The CLI in `src/htmladapt/__main__.py` is verbose. It can be simplified to be more command-line friendly and less "graphical".
- **Action:**
    - Remove `rich` progress bars, tables, and panels. Use simple `print` statements for output.
    - Remove options related to LLM.
    - Simplify the `extract` and `merge` commands.

## 5. Documentation and Tests

-   **Action:**
    -   Update `README.md` and files in `docs/` to reflect the simplified API and removed features.
    -   Remove tests for `llm`, `utils`, and other deleted features.
    -   Update existing tests to match the new simplified configuration and API.
    -   Ensure test coverage for the core functionality remains high.

## Implementation Steps

1.  **Branch:** Create a new git branch for the refactoring work (e.g., `refactor/simplification`).
2.  **Remove Modules:** Delete `src/htmladapt/llm` and `src/htmladapt/utils`.
3.  **Simplify `config.py`:** Apply the planned simplifications to `ProcessingConfig`.
4.  **Simplify `parser.py`:** Remove `validate_html` and other non-essential methods.
5.  **Simplify `matcher.py`:** Refactor the similarity calculation.
6.  **Update `tool.py`:** Remove logic related to LLM, utils, and complex config from `src/htmladapt/core/extractor_merger.py`.
7.  **Run Tests & Fix:** Run tests, see them fail, and then update them to reflect the changes. Remove tests for deleted features.
8.  **Flatten Structure:** Move files from `core` and `algorithms` to `src/htmladapt`, rename `extractor_merger.py` to `tool.py`, and update all imports.
9.  **Consolidate Entry Point:** Delete `src/htmladapt/htmladapt.py` and update `src/htmladapt/__init__.py`.
10. **Simplify CLI:** Refactor `src/htmladapt/__main__.py`.
11. **Update Documentation:** Update `README.md` and `docs/`.
12. **Final Test Run:** Ensure all tests pass.
13. **Review and Merge:** Create a pull request for review.
