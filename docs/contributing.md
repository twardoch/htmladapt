
---
title: Contributing
layout: default
nav_order: 4
parent: Home
---

# Contributing

We welcome contributions to the `htmladapt` project! Whether it's reporting a bug, suggesting a feature, or submitting code, your help is appreciated.

## Development Setup

To get started with development, follow these steps:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/twardoch/htmladapt.git
    cd htmladapt
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    # Using Python's built-in venv
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**

    Install the package in editable mode with all development and testing dependencies.

    ```bash
    pip install -e ".[dev,test,llm]"
    ```

## Running Tests

`htmladapt` includes a comprehensive test suite to ensure code quality and prevent regressions. To run the tests:

```bash
# Run all unit and integration tests
pytest

# Run tests with coverage reporting
pytest --cov=htmladapt
```

## Code Quality

We use `black` for code formatting and `ruff` for linting. Before submitting a pull request, please ensure your code adheres to the project's style guidelines.

```bash
# Format the code
black htmladapt/ tests/

# Run the linter
ruff check htmladapt/ tests/

# Run the static type checker
mypy htmladapt/
```

## Project Architecture

The codebase is organized into logical modules to facilitate development:

```
htmladapt/
├── core/                  # Core logic
│   ├── parser.py          # HTML parsing
│   ├── extractor.py       # Content extraction
│   ├── matcher.py         # Element matching algorithms
│   └── merger.py          # Content reconciliation
├── algorithms/            # Specific algorithms used by the core
│   ├── id_generation.py   # ID generation strategies
│   └── fuzzy_match.py     # Similarity scoring
├── llm/                   # LLM integration
│   └── reconciler.py      # LLM-based conflict resolution
├── utils/                 # Utility functions
│   └── html_utils.py      # HTML processing helpers
└── tests/
    ├── unit/              # Unit tests for individual components
    └── integration/       # End-to-end workflow tests
```

## Submitting Changes

1.  Create a new branch for your feature or bug fix.
2.  Make your changes and add or update tests as needed.
3.  Ensure all tests pass and the code is formatted correctly.
4.  Push your branch to GitHub and open a pull request with a clear description of your changes.
