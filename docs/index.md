# HTMLAdapt: HTML Content Extraction and Merge Tool

HTMLAdapt is a Python tool for bidirectional HTML transformation. It extracts content for editing while preserving document structure, then merges changes back without breaking formatting. Useful for translation, content updates, and HTML processing where layout must stay intact.

## Why HTMLAdapt?

Editing complex HTML documents directly is risky:

- Manual edits often break CSS or JavaScript
- Basic find-and-replace can't handle nested tags
- Most tools strip important markup or scramble the layout
- Translation software usually messes up HTML unless you enjoy cleanup duty

HTMLAdapt avoids these issues by maintaining structure throughout the edit-merge cycle.

## How It Works

The process has two steps:

### 1. Extract
Converts the source HTML into two parts:

- **Superset**: Original HTML with unique IDs added to all text elements
- **Subset**: Minimal version with only translatable content, tagged with matching IDs

```python
from htmladapt import HTMLExtractMergeTool

tool = HTMLExtractMergeTool()
map_html, comp_html = tool.extract(original_html)
```

### 2. Merge
Reapplies edited content from the subset to the superset using smart reconciliation:

```python
final_html = tool.merge(
    edited_comp_html,
    original_comp_html,
    map_html,
    original_html
)
```

## Key Features

### Structure Preservation
Keeps original HTML layout, classes, scripts, and styles untouched during content edits.

### Smart Element Matching
Matches text elements across versions using:
- Exact ID matching when possible
- Content hashing for similarity detection
- Fuzzy logic for modified text
- LLMs for tricky edge cases (optional)

### Fast Processing
Built for speed and efficiency:
- Uses lxml for parsing (faster than standard libraries)
- Hash-based matching runs in linear time
- Low memory footprint
- Configurable performance settings

### Conflict Resolution
Optional LLM integration resolves ambiguous matches that algorithms can't sort out.

### Error Resilience
Handles broken HTML, deep nesting, and other messes without crashing. Includes fallback strategies for worst-case inputs.