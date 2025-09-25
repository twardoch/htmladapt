# HTMLAdapt: HTML Content Extraction and Merge Tool

HTMLAdapt is a Python tool for bidirectional HTML document transformation that preserves structural integrity while enabling content modification through an intermediate representation. Useful for translation workflows, content editing, and HTML processing where maintaining original formatting and styling matters.

## Why HTMLAdapt?

When working with complex HTML documents that need translation or content editing, traditional approaches often fail:

- **Manual editing** risks breaking structure and styling
- **Simple find-replace** can't handle complex markup
- **Existing tools** lose formatting and hierarchy
- **Translation tools** often mangle HTML

HTMLAdapt solves these problems with algorithms that understand HTML structure and preserve it through the entire edit-merge cycle.

## How It Works

HTMLAdapt uses a two-phase workflow:

### 1. Extract Phase
Transforms the original HTML into two representations:

- **Superset Document**: Original HTML with unique IDs added to all text-containing elements
- **Subset Document**: Simplified version with only translatable content, preserving IDs

```python
from htmladapt import HTMLExtractMergeTool

tool = HTMLExtractMergeTool()
superset_html, subset_html = tool.extract(original_html)
```

### 2. Merge Phase
Recombines edited content with original structure using reconciliation algorithms:

```python
final_html = tool.merge(
    edited_subset_html,
    original_subset_html,
    superset_html,
    original_html
)
```

## Key Features

### Structure Preservation
Maintains all original HTML structure, CSS classes, JavaScript references, and formatting during content modification.

### Element Matching
Uses multiple strategies to match content between versions:
- **Perfect ID matching** for unchanged elements
- **Hash-based signatures** for content similarity
- **Fuzzy matching** for modified text
- **LLM integration** for ambiguous cases

### Performance
Optimized for large documents:
- lxml parser for speed (2-3x faster than alternatives)
- O(n) hash-based matching in most cases
- Memory-efficient processing
- Configurable performance profiles

### AI Conflict Resolution
Integrates with Large Language Models to resolve complex matching scenarios that algorithms alone cannot handle.

### Error Handling
Handles malformed HTML, deeply nested structures, and edge cases gracefully with fallback mechanisms.

## Installation

```bash
pip install htmladapt
```

Or with LLM support:

```bash
pip install htmladapt[llm]
```

## Quick Start

### Basic Usage

```python
from htmladapt import HTMLExtractMergeTool

# Initialize the tool
tool = HTMLExtractMergeTool(id_prefix="trans_")

# Step 1: Extract content
original_html = open('document.html', 'r').read()
superset_html, subset_html = tool.extract(original_html)

# Step 2: Edit the subset
edited_subset = subset_html.replace('Hello', 'Hola').replace('World', 'Mundo')

# Step 3: Merge back
final_html = tool.merge(
    edited_subset,      # Edited content
    subset_html,        # Original subset for comparison
    superset_html,      # Enhanced original with IDs
    original_html       # Original document
)

# Save result
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

# Set up LLM
llm = LLMReconciler(
    api_key=os.environ['OPENAI_API_KEY'],
    model="gpt-4o-mini"
)

tool = HTMLExtractMergeTool(llm_reconciler=llm)

# Automatic LLM use for ambiguous matches
final_html = tool.merge(edited_subset, subset_html, superset_html, original_html)
```

## Use Cases

### Website Translation
Translate content while preserving CSS classes, JavaScript, and design.

```python
# Extract content
superset, subset = tool.extract(webpage_html)

# Send to translation service
translated_subset = translation_service.translate(subset, target_lang='es')

# Merge back with styling intact
localized_webpage = tool.merge(translated_subset, subset, superset, webpage_html)
```

### Content Management
Edit HTML in a simplified interface while maintaining complex structure.

```python
# Extract for CMS
_, editable_content = tool.extract(article_html)

# User edits content
edited_content = cms.edit_interface(editable_content)

# Merge back with layout preserved
updated_article = tool.merge(edited_content, editable_content, superset, article_html)
```

### Documentation Maintenance
Update docs while preserving code highlighting and navigation.

```python
# Extract text
superset, docs_text = tool.extract(documentation_html)

# Update content
updated_text = update_documentation(docs_text)

# Merge with formatting intact
final_docs = tool.merge(updated_text, docs_text, superset, documentation_html)
```

## Architecture

HTMLAdapt uses a layered approach:

### Layer 1: HTML Parsing
- **Primary**: BeautifulSoup with lxml backend
- **Fallback**: html.parser for malformed HTML
- **Error Recovery**: Automatic tag closure and structure repair

### Layer 2: ID Generation
- **Base36 encoding** for compact IDs
- **Hierarchical numbering** for traceability
- **Collision detection** and prevention

### Layer 3: Matching Strategies
1. **Perfect Matching**: Identical ID preservation (fastest)
2. **Hash Matching**: Content signature comparison (fast)
3. **Fuzzy Matching**: Similarity scoring with difflib (accurate)
4. **LLM Matching**: Semantic understanding for edge cases (most accurate)

### Layer 4: Structural Analysis
- **LCS algorithms** for sequence reordering
- **Tree diff** algorithms for hierarchical changes
- **Conflict identification** for manual resolution

### Layer 5: Reconciliation
- **Three-way merge** logic from version control
- **Contextual conflict resolution** with minimal LLM calls
- **Fallback heuristics** for offline operation

## Performance

| Document Size | Processing Time | Memory Usage | Recommended Profile |
|---------------|----------------|--------------|-------------------|
| < 1MB         | ~100ms         | 4-8MB        | balanced         |
| 1-10MB        | ~1-5s          | 20-80MB      | fast             |
| > 10MB        | ~5-30s         | 100-400MB    | fast             |

## Error Handling

HTMLAdapt handles common issues:

- **Malformed tags**: Automatic closure and repair
- **Deeply nested structures**: Configurable depth limits
- **Large documents**: Memory-efficient streaming
- **Encoding issues**: Automatic detection and conversion
- **Missing elements**: Fallback matching

## Testing

HTMLAdapt includes comprehensive test suites:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=htmladapt tests/

# Performance benchmarks
pytest tests/benchmarks/
```

Test categories:
- **Unit tests** for components
- **Integration tests** for workflows
- **Performance tests** with various document sizes
- **Edge case tests** for malformed HTML
- **Round-trip tests** for content preservation

## API Reference

### Core Classes

#### `HTMLExtractMergeTool`
Main interface for extraction and merging.

**Methods:**
- `extract(html: str) -> Tuple[str, str]`: Create superset and subset
- `merge(edited: str, subset: str, superset: str, original: str) -> str`: Merge content

#### `ProcessingConfig`
Configuration object.

**Parameters:**
- `id_prefix: str`: ID prefix (default: "auto_")
- `similarity_threshold: float`: Minimum similarity for fuzzy matching (default: 0.7)
- `enable_llm_resolution: bool`: Use LLM for conflicts (default: False)
- `performance_profile: str`: fast|balanced|accurate (default: "balanced")

#### `LLMReconciler`
LLM conflict resolution interface.

**Parameters:**
- `api_key: str`: OpenAI API key
- `model: str`: Model name (default: "gpt-4o-mini")
- `max_context_tokens: int`: Maximum tokens per request (default: 1000)

### Utility Functions

```python
from htmladapt.utils import (
    validate_html,
    estimate_processing_time,
    optimize_for_size
)

# Validate HTML
is_valid, issues = validate_html(html_content)

# Estimate processing time
time_estimate, memory_estimate = estimate_processing_time(html_content)

# Optimize large documents
optimized_html = optimize_for_size(html_content, target_size_mb=5)
```

## Integration Examples

### Flask Application

```python
from flask import Flask, request, jsonify
from htmladapt import HTMLExtractMergeTool

app = Flask(__name__)
tool = HTMLExtractMergeTool()

@app.route('/extract', methods=['POST'])
def extract_content():
    html = request.json['html']
    superset, subset = tool.extract(html)
    return jsonify({
        'superset': superset,
        'subset': subset
    })

@app.route('/merge', methods=['POST'])
def merge_content():
    data = request.json
    result = tool.merge(
        data['edited'],
        data['subset'],
        data['superset'],
        data['original']
    )
    return jsonify({'result': result})
```

### Django Integration

```python
# models.py
from django.db import models

class Document(models.Model):
    original_html = models.TextField()
    superset_html = models.TextField()
    subset_html = models.TextField()

    def extract_content(self):
        from htmladapt import HTMLExtractMergeTool
        tool = HTMLExtractMergeTool()
        self.superset_html, self.subset_html = tool.extract(self.original_html)
        self.save()

    def merge_content(self, edited_html):
        from htmladapt import HTMLExtractMergeTool
        tool = HTMLExtractMergeTool()
        return tool.merge(
            edited_html,
            self.subset_html,
            self.superset_html,
            self.original_html
        )
```

### Celery Processing

```python
from celery import Celery
from htmladapt import HTMLExtractMergeTool

app = Celery('htmladapt_tasks')
tool = HTMLExtractMergeTool()

@app.task
def process_large_document(html_content, user_id):
    try:
        superset, subset = tool.extract(html_content)
        return {'status': 'success', 'subset_id': store_subset(subset)}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.task
def merge_edited_content(edited_html, subset_html, superset_html, original_html):
    result = tool.merge(edited_html, subset_html, superset_html, original_html)
    return result
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/htmladapt.git
cd htmladapt

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,test,llm]"

# Run tests
pytest

# Run type checking
mypy htmladapt/

# Format code
black htmladapt/
ruff check htmladapt/
```

### Code Structure

```
htmladapt/
├── core/
│   ├── parser.py          # HTML parsing
│   ├── extractor.py       # Content extraction
│   ├── matcher.py         # Element matching
│   └── merger.py          # Content reconciliation
├── algorithms/
│   ├── id_generation.py   # ID generation
│   ├── tree_diff.py       # Tree comparison
│   └── fuzzy_match.py     # Similarity scoring
├── llm/
│   ├── reconciler.py      # LLM integration
│   └── prompts.py         # Prompt templates
├── utils/
│   ├── html_utils.py      # HTML utilities
│   └── performance.py    # Performance optimization
└── tests/
    ├── unit/              # Unit tests
    ├── integration/       # Integration tests
    └── benchmarks/        # Performance tests
```

## License

MIT License - see [LICENSE](LICENSE) file.

## Support

- **Documentation**: [https://htmladapt.readthedocs.io](https://htmladapt.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/yourusername/htmladapt/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/htmladapt/discussions)
- **Email**: support@htmladapt.dev

## Citation

For academic use:

```bibtex
@software{htmladapt2024,
  title={HTMLAdapt: HTML Content Extraction and Merge Tool},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/htmladapt}
}
```