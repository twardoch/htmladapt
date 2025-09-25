---
layout: default
title: Usage
nav_order: 2
---

# Quick Start

## Installation

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
superset_html, subset_html = tool.extract(original_html)

# Step 2: Edit the subset (translate, modify content, etc.)
# This is where you would integrate your translation workflow
edited_subset = subset_html.replace('Hello', 'Hola').replace('World', 'Mundo')

# Step 3: Merge edited content back into original structure
final_html = tool.merge(
    edited_subset,      # Your edited content
    subset_html,        # Original subset for comparison
    superset_html,      # Enhanced original with IDs
    original_html       # Original document
)

# Save the result
with open('translated_document.html', 'w') as f:
    f.write(final_html)
```

### Advanced Configuration

```python
from htmladapt import HTMLExtractMergeTool, ProcessingConfig

# Custom configuration
config = ProcessingConfig(
    id_prefix="my_prefix_",
    similarity_threshold=0.8,
    enable_llm_resolution=True,
    llm_model="gpt-4o-mini",
    performance_profile="accurate"  # fast|balanced|accurate
)

tool = HTMLExtractMergeTool(config=config)
```

### With LLM Integration

```python
import os
from htmladapt import HTMLExtractMergeTool, LLMReconciler

# Set up LLM for conflict resolution
llm = LLMReconciler(
    api_key=os.environ['OPENAI_API_KEY'],
    model="gpt-4o-mini"
)

tool = HTMLExtractMergeTool(llm_reconciler=llm)

# The tool will automatically use LLM for ambiguous matches
final_html = tool.merge(edited_subset, subset_html, superset_html, original_html)
```

## Use Cases

### **Website Translation**
Translate website content while preserving all CSS classes, JavaScript functionality, and visual design.

```python
# Extract translatable content
superset, subset = tool.extract(webpage_html)

# Send subset to translation service
translated_subset = translation_service.translate(subset, target_lang='es')

# Merge back maintaining all original styling
localized_webpage = tool.merge(translated_subset, subset, superset, webpage_html)
```

### **Content Management**
Edit HTML content in a simplified interface while maintaining complex original structure.

```python
# Extract editable content for CMS
_, editable_content = tool.extract(article_html)

# User edits in simplified interface
edited_content = cms.edit_interface(editable_content)

# Merge back preserving article layout and styling
updated_article = tool.merge(edited_content, editable_content, superset, article_html)
```

### **Documentation Maintenance**
Update technical documentation while preserving code highlighting, navigation, and styling.

```python
# Extract documentation text
superset, docs_text = tool.extract(documentation_html)

# Update content while preserving code blocks and formatting
updated_text = update_documentation(docs_text)

# Merge maintaining syntax highlighting and navigation
final_docs = tool.merge(updated_text, docs_text, superset, documentation_html)
```