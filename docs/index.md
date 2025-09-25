
---
title: Home
layout: default
nav_order: 1
---

# HTMLAdapt

**Intelligent HTML Content Extraction and Merge Tool**

HTMLAdapt is a Python-based tool for bidirectional HTML document transformation. It preserves structural integrity while enabling seamless content modification through an intermediate representation. It's perfect for translation workflows, content editing, and any HTML processing where maintaining original formatting and styling is critical.

---

## Why HTMLAdapt?

When working with complex HTML documents that need translation or content editing, traditional approaches often fall short:

- **Manual editing** risks breaking the document's structure and styling.
- **Simple find-and-replace** can't handle complex or nested markup patterns.
- **Most translation tools** mangle HTML or require extensive and costly post-processing.

HTMLAdapt solves these challenges with intelligent algorithms that understand and preserve HTML structure through the entire edit-merge cycle.

## How It Works

HTMLAdapt uses a sophisticated two-phase workflow:

1.  **Extract Phase**: Transforms a complex HTML document into two complementary versions:
    *   **Superset Document**: The original HTML enhanced with unique IDs on all text-containing elements.
    *   **Subset Document**: A lightweight version containing only the translatable content, with IDs preserved for mapping.

2.  **Merge Phase**: Intelligently recombines the edited (e.g., translated) subset with the original structure using advanced reconciliation algorithms.

---

## Quick Start

Here is a minimal example of how to use `htmladapt`:

```python
from htmladapt import HTMLExtractMergeTool

# Initialize the tool
tool = HTMLExtractMergeTool(id_prefix="trans_")

# 1. Read the original HTML from a file
with open('document.html', 'r', encoding='utf-8') as f:
    original_html = f.read()

# 2. Extract content into superset and subset documents
superset_html, subset_html = tool.extract(original_html)

# 3. Edit the subset (e.g., translate, modify content)
# In a real workflow, you would send `subset_html` to a translation service.
edited_subset = subset_html.replace('Hello', 'Hola').replace('World', 'Mundo')

# 4. Merge the edited content back into the original structure
final_html = tool.merge(
    edited=edited_subset,
    subset=subset_html,
    superset=superset_html,
    original=original_html
)

# 5. Save the final, merged HTML
with open('translated_document.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("Translation complete! Check 'translated_document.html'.")
```
