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

The codebase is organized as follows:

```
htmladapt/
├── src/
│   └── htmladapt/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.py
│       ├── id_generation.py
│       ├── matcher.py
│       ├── parser.py
│       └── tool.py
└── tests/
    ├── test_config.py
    ├── test_extractor_merger.py
    ├── test_id_generation.py
    ├── test_integration.py
    ├── test_package.py
    └── test_parser.py
```
