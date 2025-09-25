---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://just-the-docs.github.io/just-the-docs/docs/navigation-structure/

layout: default
title: Home
nav_order: 1
---

# HTMLAdapt: Intelligent HTML Content Extraction and Merge Tool

HTMLAdapt is a Python-based tool for bidirectional HTML document transformation that preserves structural integrity while enabling seamless content modification through an intermediate representation. Perfect for translation workflows, content editing, and HTML processing where maintaining original formatting and styling is critical.

## Why HTMLAdapt?

When working with complex HTML documents that need translation or content editing, traditional approaches fall short:

- **Manual editing** risks breaking structure and styling
- **Simple find-replace** can't handle complex markup patterns
- **Existing tools** lose crucial formatting and hierarchical relationships
- **Translation tools** often mangle HTML or require extensive post-processing

HTMLAdapt solves these challenges with intelligent algorithms that understand HTML structure and preserve it through the entire edit-merge cycle.

## How It Works

HTMLAdapt implements a sophisticated two-phase workflow:

### 1. Extract Phase
Transforms a complex original HTML document into two complementary representations:

- **Superset Document**: The original HTML enhanced with unique IDs on all text-containing elements
- **Subset Document**: A lightweight version containing only translatable content with preserved IDs

```python
from htmladapt import HTMLExtractMergeTool

tool = HTMLExtractMergeTool()
superset_html, subset_html = tool.extract(original_html)
```

### 2. Merge Phase
Intelligently recombines edited content with the original structure using advanced reconciliation algorithms:

```python
final_html = tool.merge(
    edited_subset_html,
    original_subset_html,
    superset_html,
    original_html
)
```

## Key Features

### **Perfect Structure Preservation**
Maintains all original HTML structure, CSS classes, JavaScript references, and formatting while allowing content modification.

### **Intelligent Element Matching**
Uses multiple sophisticated algorithms to match content between versions:
- **Perfect ID matching** for unchanged elements
- **Hash-based signatures** for content similarity
- **Fuzzy matching** for modified text
- **LLM integration** for ambiguous cases

### **High Performance**
Optimized for large documents with:
- lxml parser for speed (2-3x faster than alternatives)
- O(n) hash-based matching for most cases
- Memory-efficient processing
- Configurable performance profiles

### **AI-Powered Conflict Resolution**
Integrates with Large Language Models to resolve complex matching scenarios that pure algorithms cannot handle.

### **Robust Error Handling**
Handles malformed HTML, deeply nested structures, and edge cases gracefully with comprehensive fallback mechanisms.