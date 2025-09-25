Here's the revised version of your document with editorial improvements for clarity, precision, and conciseness:

---

---
layout: default
title: Usage
nav_order: 2
---

# Quick Start

## Installation

Install the base package:

```bash
pip install htmladapt
```

Or install with LLM support:

```bash
pip install htmladapt[llm]
```

## Basic Usage

```python
from htmladapt import HTMLExtractMergeTool

# Initialize the tool
tool = HTMLExtractMergeTool(id_prefix="trans_")

# Step 1: Extract content from original HTML
original_html = open('document.html', 'r').read()
map_html, comp_html = tool.extract(original_html)

# Step 2: Edit the subset (e.g., translate or modify)
cnew_path = comp_html.replace('Hello', 'Hola').replace('World', 'Mundo')

# Step 3: Merge edited content back into the original structure
final_html = tool.merge(
    cnew_path,   # Modified content
    comp_html,     # Original extracted subset
    map_html,   # Original HTML with added IDs
    original_html    # Unchanged original HTML
)

# Save result
with open('translated_document.html', 'w') as f:
    f.write(final_html)
```

## Advanced Configuration

```python
from htmladapt import HTMLExtractMergeTool, ProcessingConfig

config = ProcessingConfig(
    id_prefix="my_prefix_",
    simi_level=0.8,
    llm_use=True,
    model_llm="gpt-4o-mini",
    perf="accurate"  # Options: fast, balanced, accurate
)

tool = HTMLExtractMergeTool(config=config)
```

## LLM Integration

```python
import os
from htmladapt import HTMLExtractMergeTool, LLMReconciler

# Configure LLM for conflict resolution
llm = LLMReconciler(
    api_key=os.environ['OPENAI_API_KEY'],
    model="gpt-4o-mini"
)

tool = HTMLExtractMergeTool(llm_reconciler=llm)

# Ambiguous matches will now be resolved using the LLM
final_html = tool.merge(cnew_path, comp_html, map_html, original_html)
```

## Use Cases

### Website Translation

Translate content without breaking styles or scripts.

```python
superset, subset = tool.extract(webpage_html)

translated_subset = translation_service.translate(subset, target_lang='es')

localized_webpage = tool.merge(translated_subset, subset, superset, webpage_html)
```

### Content Management

Edit content in a clean interface while keeping layout intact.

```python
_, editable_content = tool.extract(article_html)

edited_content = cms.edit_interface(editable_content)

updated_article = tool.merge(edited_content, editable_content, superset, article_html)
```

### Documentation Maintenance

Update documentation text without disturbing formatting or navigation.

```python
superset, docs_text = tool.extract(documentation_html)

updated_text = update_documentation(docs_text)

final_docs = tool.merge(updated_text, docs_text, superset, documentation_html)
```

--- 

Let me know if you'd like to tailor this for a specific audience or purpose.