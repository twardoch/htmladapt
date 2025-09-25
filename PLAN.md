# HTMLAdapt Improvement Plan

the_file: PLAN.md

## Objective
Deliver small, high-impact fixes that improve merge correctness and respect user configuration without adding new complexity.

## Priorities

1. **Fix inline formatting merge bug**
   - Add a regression test that covers translations affecting inline elements (e.g., `<p>Text <strong>x</strong></p>`).
   - Update `_apply_changes_to_superset` to replace descendant text safely so the translated content reaches nested tags.
   - Verify existing tests and the new test pass.

2. **Honor configured parser preference**
   - Add coverage proving that `ProcessingConfig.parser_preference` controls the builder used for superset/subset creation.
   - Refactor `_create_superset` and `_create_subset` to reuse the parser actually selected during `parse`.
   - Ensure malformed-html fallbacks still work after the change.

3. **Enable LLM reconciliation path when requested**
   - Introduce a minimal interface/type hint for reconcilers.
   - Update the merge pipeline to call the reconciler when similarity scores fall below the acceptance threshold and `enable_llm_resolution` is true.
   - Extend tests with a stub reconciler to confirm the hook executes and its result influences matching.

4. **Tighten supporting ergonomics** (only as needed for work above)
   - Replace broad `except Exception` logging with narrower error handling where failures are expected.
   - Trim unused parsing (e.g., redundant `original_soup`) if it becomes dead code during refactors.

## Done Definition
- All new tests pass with `uvx hatch test`.
- PLAN, TODO, WORK updated to reflect progress.
- Changes remain small, readable, and keep the tool performant.
