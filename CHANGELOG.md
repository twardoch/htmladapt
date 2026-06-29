# Changelog

All notable changes to htmladapt are documented here.

## [1.0.13] — 2025-01-01

### Added
- Initial public release on PyPI as `htmladapt`
- `HTMLExtractMergeTool`: two-phase extract/merge workflow for bidirectional HTML transformation
- `ProcessingConfig` dataclass for configuring ID prefix and similarity threshold
- Multi-strategy element matching: perfect ID, hash-based, and fuzzy (rapidfuzz)
- `IDGenerator` with base36 encoding, collision detection, and element-hint prefixes
- `HTMLParser` with automatic lxml → html5lib → html.parser fallback chain
- CLI (`htmladapt extract` / `htmladapt merge`) via `python-fire`
- Full test suite (38 tests) covering unit, integration, and round-trip scenarios
- GitHub Actions CI: ruff lint + format check, pytest on Python 3.10/3.11/3.12, build verification
- Jekyll documentation site (just-the-docs theme) at `docs/`
- `hatch-vcs` for tag-based semver versioning
- `ruff` and `mypy` configuration in `pyproject.toml`
