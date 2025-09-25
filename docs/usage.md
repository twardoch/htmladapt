
---
title: Usage Guide
layout: default
nav_order: 2
parent: Home
---

# Usage Guide

This guide provides detailed instructions on how to install, configure, and use the `htmladapt` package for your content transformation workflows.

## Installation

Install the package from PyPI using `pip`.

```bash
pip install htmladapt
```

For workflows requiring AI-powered conflict resolution, install with the optional `llm` dependencies:

```bash
pip install htmladapt[llm]
```

## Basic Workflow

The core workflow consists of three steps: **extract**, **edit**, and **merge**.

```python
from htmladapt import HTMLExtractMergeTool

# Initialize the tool
tool = HTMLExtractMergeTool()

# 1. EXTRACT: Create the superset and subset
original_html = "<html><body><p>Hello World</p></body></html>"
superset_html, subset_html = tool.extract(original_html)

# At this point, you would save `subset_html` and send it for translation
# or editing.

# 2. EDIT: Simulate an edit on the subset content
edited_subset_html = subset_html.replace("Hello World", "Hola Mundo")

# 3. MERGE: Recombine the edited content with the original structure
final_html = tool.merge(
    edited=edited_subset_html,
    subset=subset_html,
    superset=superset_html,
    original=original_html
)

# The final_html will be: "<html><body><p>Hola Mundo</p></body></html>"
print(final_html)
```

## Advanced Configuration

You can customize the behavior of `htmladapt` by passing a `ProcessingConfig` object during initialization.

```python
from htmladapt import HTMLExtractMergeTool, ProcessingConfig

# Define a custom configuration
config = ProcessingConfig(
    id_prefix="my-prefix_",
    similarity_threshold=0.8,
    enable_llm_resolution=True,
    llm_model="gpt-4o-mini",
    performance_profile="accurate"  # Options: fast|balanced|accurate
)

tool = HTMLExtractMergeTool(config=config)
```

## LLM Integration

For complex documents where content may be significantly reordered or rephrased, `htmladapt` can use a Large Language Model (LLM) to resolve ambiguous matches.

```python
import os
from htmladapt import HTMLExtractMergeTool, LLMReconciler

# Set up the LLM reconciler with your API key
llm = LLMReconciler(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o-mini"
)

# Initialize the tool with the reconciler
tool = HTMLExtractMergeTool(llm_reconciler=llm)

# The tool will now automatically use the LLM for ambiguous cases
# during the merge process.
final_html = tool.merge(edited_subset, subset_html, superset_html, original_html)
```

## Use Cases

### Website Translation

Translate website content while perfectly preserving all CSS classes, JavaScript functionality, and visual design.

```python
# Extract translatable content from a webpage
superset, subset = tool.extract(webpage_html)

# Send subset to a translation service
translated_subset = my_translation_api.translate(subset, target_lang='es')

# Merge back to create the localized webpage
languages_webpage = tool.merge(translated_subset, subset, superset, webpage_html)
```

### Content Management Systems (CMS)

Allow users to edit HTML content in a simplified interface (like a Markdown editor) while maintaining the complex original structure.

```python
# Extract editable content for the CMS
_, editable_content = tool.extract(article_html)

# User edits the content in a simplified interface
edited_content = cms.edit_interface(editable_content)

# Merge the changes back, preserving the article's layout and styling
updated_article = tool.merge(edited_content, editable_content, superset, article_html)
```
