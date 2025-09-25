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

## Installation

```bash
pip install htmladapt
```

Or install with LLM support:

```bash
pip install htmladapt[llm]
```

## Quick Start

### Basic Usage

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

## Architecture Deep Dive

HTMLAdapt uses a multi-layered approach to ensure reliable HTML processing:

### Layer 1: Robust HTML Parsing
- **Primary**: BeautifulSoup with lxml backend for performance
- **Fallback**: html.parser for malformed HTML
- **Error Recovery**: Automatic tag closure and structure repair

### Layer 2: Intelligent ID Generation
- **Base36 encoding** for compact, collision-free IDs
- **Hierarchical numbering** for traceability
- **Collision detection** and prevention

### Layer 3: Multi-Strategy Matching
1. **Perfect Matching**: Identical ID preservation (fastest)
2. **Hash Matching**: Content signature comparison (fast)
3. **Fuzzy Matching**: Similarity scoring with difflib (accurate)
4. **LLM Matching**: Semantic understanding for edge cases (most accurate)

### Layer 4: Structural Analysis
- **LCS algorithms** for sequence reordering detection
- **Tree diff** algorithms for hierarchical changes
- **Conflict identification** for manual resolution

### Layer 5: Smart Reconciliation
- **Three-way merge** logic from version control systems
- **Contextual conflict resolution** using minimal LLM calls
- **Fallback heuristics** for offline operation

## Performance Characteristics

| Document Size | Processing Time | Memory Usage | Recommended Profile |
|---------------|----------------|--------------|-------------------|
| < 1MB         | ~100ms         | 4-8MB        | balanced         |
| 1-10MB        | ~1-5s          | 20-80MB      | fast             |
| > 10MB        | ~5-30s         | 100-400MB    | fast             |

## Error Handling

HTMLAdapt gracefully handles common HTML issues:

- **Malformed tags**: Automatic closure and repair
- **Deeply nested structures**: Configurable depth limits
- **Large documents**: Memory-efficient streaming
- **Encoding issues**: Automatic detection and conversion
- **Missing elements**: Intelligent fallback matching

## Testing and Quality Assurance

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
- **Unit tests** for individual components
- **Integration tests** for end-to-end workflows
- **Performance tests** with various document sizes
- **Edge case tests** for malformed HTML
- **Round-trip tests** to ensure content preservation

## API Reference

### Core Classes

#### `HTMLExtractMergeTool`
Main interface for extraction and merging operations.

**Methods:**
- `extract(html: str) -> Tuple[str, str]`: Create superset and subset
- `merge(edited: str, subset: str, superset: str, original: str) -> str`: Merge content

#### `ProcessingConfig`
Configuration object for customizing behavior.

**Parameters:**
- `id_prefix: str`: Prefix for generated IDs (default: "auto_")
- `similarity_threshold: float`: Minimum similarity for fuzzy matching (default: 0.7)
- `enable_llm_resolution: bool`: Use LLM for conflicts (default: False)
- `performance_profile: str`: Processing profile - fast|balanced|accurate (default: "balanced")

#### `LLMReconciler`
Interface for LLM-powered conflict resolution.

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

# Validate HTML before processing
is_valid, issues = validate_html(html_content)

# Estimate processing requirements
time_estimate, memory_estimate = estimate_processing_time(html_content)

# Optimize large documents
optimized_html = optimize_for_size(html_content, target_size_mb=5)
```

## Integration Examples

### Flask Web Application

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

### Celery Background Processing

```python
from celery import Celery
from htmladapt import HTMLExtractMergeTool

app = Celery('htmladapt_tasks')
tool = HTMLExtractMergeTool()

@app.task
def process_large_document(html_content, user_id):
    try:
        superset, subset = tool.extract(html_content)
        # Store results or notify user
        return {'status': 'success', 'subset_id': store_subset(subset)}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.task
def merge_edited_content(edited_html, subset_html, superset_html, original_html):
    result = tool.merge(edited_html, subset_html, superset_html, original_html)
    return result
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/htmladapt.git
cd htmladapt

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

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

### Architecture for Contributors

The codebase is organized into logical modules:

```
htmladapt/
├── core/
│   ├── parser.py          # HTML parsing logic
│   ├── extractor.py       # Content extraction
│   ├── matcher.py         # Element matching algorithms
│   └── merger.py          # Content reconciliation
├── algorithms/
│   ├── id_generation.py   # ID generation strategies
│   ├── tree_diff.py       # Tree comparison algorithms
│   └── fuzzy_match.py     # Similarity scoring
├── llm/
│   ├── reconciler.py      # LLM integration
│   └── prompts.py         # Prompt templates
├── utils/
│   ├── html_utils.py      # HTML processing utilities
│   └── performance.py    # Performance optimization
└── tests/
    ├── unit/              # Unit tests
    ├── integration/       # Integration tests
    └── benchmarks/        # Performance tests
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support and Community

- **Documentation**: [https://htmladapt.readthedocs.io](https://htmladapt.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/yourusername/htmladapt/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/htmladapt/discussions)
- **Email**: support@htmladapt.dev

## Citation

If you use HTMLAdapt in academic research, please cite:

```bibtex
@software{htmladapt2024,
  title={HTMLAdapt: Intelligent HTML Content Extraction and Merge Tool},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/htmladapt}
}
```

---

**HTMLAdapt** - Making HTML content transformation intelligent, reliable, and effortless.