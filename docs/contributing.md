---
layout: default
title: Contributing
nav_order: 4
---

# Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

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

### Codebase Structure

```
htmladapt/
├── core/
│   ├── parser.py          # HTML parsing
│   ├── extractor.py       # Content extraction
│   ├── matcher.py         # Element matching
│   └── merger.py          # Content merging
├── algorithms/
│   ├── id_generation.py   # ID generation
│   ├── tree_diff.py       # Tree comparison
│   └── fuzzy_match.py     # Similarity scoring
├── llm/
│   ├── reconciler.py      # LLM integration
│   └── prompts.py        # Prompt templates
├── utils/
│   ├── html_utils.py      # HTML utilities
│   └── performance.py    # Performance tools
└── tests/
    ├── unit/             # Unit tests
    ├── integration/      # Integration tests
    └── benchmarks/       # Performance benchmarks
```