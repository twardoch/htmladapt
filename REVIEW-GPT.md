# HTMLAdapt Code Review

## Critical Findings

1. **Translated inline content is not propagated into nested elements**  
   - Location: `src/htmladapt/core/extractor_merger.py:280-302`  
   - During merge the code only strips top-level `NavigableString` nodes before inserting the translated text, leaving any nested tags untouched. When translating markup such as `<p>Prefix <strong>Inner</strong> Suffix</p>`, the resulting HTML becomes `Translated<strong>Inner</strong>`—the inner text never updates.  
   - Repro:  
     ```python
     tool = HTMLExtractMergeTool()
     html = """<html><body><p>Prefix <strong>Inner</strong> Suffix</p></body></html>"""
     superset, subset = tool.extract(html)
     merged = tool.merge(subset.replace("Prefix Inner Suffix", "Translated"), subset, superset, html)
     assert "<strong>Inner" not in merged  # currently fails
     ```
   - Impact: Any sentence containing inline formatting (links, emphasis, spans) keeps the old inner text, breaking translation workflows.  
   - Suggested fix: replace the target element entirely (e.g., via `superset_elem.clear(); superset_elem.append(...)`) or walk both trees to rewrite descendant text nodes according to the subset edits.

2. **Configured parser preference is ignored when rebuilding the superset/subset soups**  
   - Location: `src/htmladapt/core/extractor_merger.py:147-148` and `src/htmladapt/core/extractor_merger.py:163-170`  
   - Both `_create_superset` and `_create_subset` hard-code `features=self.parser._available_parsers[0]`, which is the detection order (`["lxml", "html5lib", "html.parser"]`). This bypasses `ProcessingConfig.parser_preference`. Users requesting `html.parser` to preserve whitespace, or falling back to `html5lib` because `lxml` chokes on malformed markup, still get forced through `lxml` here, reintroducing the failure the initial parse already avoided.  
   - Suggested fix: capture the builder actually used during `parse` (e.g., `soup.builder.name`) or reuse the original soup through `copy.copy`/`copy.deepcopy`, so the configured preference is honored consistently.

3. **LLM reconciliation path is never invoked**  
   - Location: `src/htmladapt/core/extractor_merger.py:24-41` (initialisation) with no subsequent references  
   - `HTMLExtractMergeTool` accepts `llm_reconciler` and exposes `ProcessingConfig.enable_llm_resolution`, yet the merge pipeline never calls into `self.llm_reconciler`. The advertised AI conflict-resolution feature is therefore dead code.  
   - Suggested fix: when `enable_llm_resolution` is true and matcher confidence is below threshold, pass the candidate texts to `LLMReconciler.resolve_conflict` and apply its decision. Add coverage that toggles the config and asserts the reconciler is invoked.

## Additional Recommendations

- Add regression tests covering inline formatting translation (e.g., `<p>Text <em>inline</em></p>`) to `tests/test_extractor_merger.py` so the merge bug surfaces.
- Consider exposing a documented API rather than reaching into `HTMLParser._available_parsers`; a public helper that returns a preferred parser name would make `_create_superset` more robust.
- Tighten validation around the rapidly growing `_used_ids` pool or reset it per document to prevent unbounded ID growth when the same tool instance processes many files.
