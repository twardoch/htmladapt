# HTMLAdapt Code Review

## Critical Findings

1. **Translated inline content is not propagated into nested elements**  
   - Location: `src/htmladapt/core/extractor_merger.py:280-302`  
   - During merge, only top-level `NavigableString` nodes are stripped before inserting translated text. Nested tags remain untouched. For markup like `<p>Prefix <strong>Inner</strong> Suffix</p>`, the result is `Translated<strong>Inner</strong>`—inner text stays unchanged.  
   - Repro:  
     ```python
     tool = HTMLExtractMergeTool()
     html = """<html><body><p>Prefix <strong>Inner</strong> Suffix</p></body></html>"""
     superset, subset = tool.extract(html)
     merged = tool.merge(subset.replace("Prefix Inner Suffix", "Translated"), subset, superset, html)
     assert "<strong>Inner" not in merged  # currently fails
     ```
   - Impact: Sentences with inline formatting (links, emphasis, spans) retain original inner text, breaking translation workflows.  
   - Fix: Replace the target element entirely (`superset_elem.clear(); superset_elem.append(...)`) or traverse both trees to update descendant text nodes according to subset edits.

2. **Parser preference ignored when rebuilding soups**  
   - Location: `src/htmladapt/core/extractor_merger.py:147-148` and `src/htmladapt/core/extractor_merger.py:163-170`  
   - `_create_superset` and `_create_subset` hard-code `features=self.parser._available_parsers[0]`, using detection order (`["lxml", "html5lib", "html.parser"]`). This overrides `ProcessingConfig.parser_preference`. Users requesting `html.parser` for whitespace preservation or `html5lib` for malformed markup still get forced through `lxml`, reintroducing issues the initial parse avoided.  
   - Fix: Capture the builder used during `parse` (e.g., `soup.builder.name`) or reuse the original soup via `copy.copy`/`copy.deepcopy` to maintain consistent parser behavior.

3. **LLM reconciliation path is unused**  
   - Location: `src/htmladapt/core/extractor_merger.py:24-41` (initialization) with no further references  
   - `HTMLExtractMergeTool` accepts `llm_reconciler` and exposes `ProcessingConfig.enable_llm_resolution`, but the merge pipeline never calls `self.llm_reconciler`. The AI conflict-resolution feature is dead code.  
   - Fix: When `enable_llm_resolution` is true and matcher confidence is low, pass candidate texts to `LLMReconciler.resolve_conflict` and apply its output. Add tests that toggle the config and verify reconciler invocation.

## Additional Recommendations

- Add regression tests for inline formatting translation (e.g., `<p>Text <em>inline</em></p>`) to `tests/test_extractor_merger.py` to expose the merge bug.
- Replace direct access to `HTMLParser._available_parsers` with a public API method that returns the preferred parser name.
- Limit growth of `_used_ids` or reset it per document to prevent unbounded ID accumulation when processing multiple files with the same tool instance.