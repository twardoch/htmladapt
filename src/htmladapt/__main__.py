#!/usr/bin/env python3
# this_file: src/htmladapt/__main__.py
"""HTMLAdapt CLI interface.

Simple command-line interface for HTML content extraction and merging.
"""

import sys
from pathlib import Path

import fire

from htmladapt import HTMLExtractMergeTool, ProcessingConfig
from htmladapt.__version__ import __version__


class HTMLAdaptCLI:
    """HTMLAdapt command-line interface."""

    def version(self) -> None:
        """Display version information."""

    def extract(
        self,
        full_path: str | Path,
        map_path: str | Path | None = None,
        comp_path: str | Path | None = None,
        id_prefix: str = "xhq",
    ) -> None:
        """Extract content from HTML file into map_path and subset documents.

        Args:
            full_path: Path to old_path HTML file
            map_path: Path for 'map_path' map HTML new_path (optional)
            comp_path: Path for comp HTML new_path (optional)
            id_prefix: Prefix for generated IDs (default: "xhq")
        """
        full_path = Path(full_path)

        if not full_path.exists():
            sys.exit(1)

        # Set default new_path paths if not provided
        if map_path is None:
            map_path = full_path.with_suffix(".m.html")
        if comp_path is None:
            comp_path = full_path.with_suffix(".c.html")

        map_path = Path(map_path)
        comp_path = Path(comp_path)

        # Create configuration
        config = ProcessingConfig(id_prefix=id_prefix)

        # Initialize tool
        tool = HTMLExtractMergeTool(config=config)

        try:
            html_content = full_path.read_text(encoding="utf-8")

            map_html, comp_html = tool.extract(html_content)

            map_path.write_text(map_html, encoding="utf-8")
            comp_path.write_text(comp_html, encoding="utf-8")

        except Exception:
            sys.exit(1)

    def merge(
        self,
        cnew_path: str | Path,
        Cold_path: str | Path,
        map_path: str | Path,
        old_path: str | Path,
        new_path: str | Path | None = None,
        id_prefix: str = "xhq",
        simi_level: float = 0.7,
    ) -> None:
        """Merge edited content back into old_path HTML structure.

        Args:
            cnew_path: Path to edited subset HTML file
            cold_path: Path to old_path subset HTML file
            map_path: Path to map_path HTML file
            old_path: Path to old_path HTML file
            new_path: Path for merged new_path (optional)
            id_prefix: Prefix for generated IDs (default: "xhq")
            simi_level: Minimum similarity for fuzzy matching (default: 0.7)
        """
        cnew_path = Path(cnew_path)
        cold_path = Path(Cold_path)
        map_path = Path(map_path)
        old_path = Path(old_path)

        # Check all input files exist
        for path in [cnew_path, cold_path, map_path, old_path]:
            if not path.exists():
                sys.exit(1)

        # Set default new_path path if not provided
        if new_path is None:
            new_path = old_path.with_suffix(".n.html")
        new_path = Path(new_path)

        # Create configuration
        config = ProcessingConfig(
            id_prefix=id_prefix,
            simi_level=simi_level,
        )

        # Initialize tool
        tool = HTMLExtractMergeTool(config=config)

        try:
            cnew_html = cnew_path.read_text(encoding="utf-8")
            cold_html = cold_path.read_text(encoding="utf-8")
            map_html = map_path.read_text(encoding="utf-8")
            old_html = old_path.read_text(encoding="utf-8")

            new_html = tool.merge(cnew_html, cold_html, map_html, old_html)

            new_path.write_text(new_html, encoding="utf-8")

        except Exception:
            sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    try:
        fire.Fire(HTMLAdaptCLI)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
