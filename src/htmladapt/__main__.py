#!/usr/bin/env python3
# this_file: src/htmladapt/__main__.py
"""HTMLAdapt CLI interface.

Command-line interface for the HTMLAdapt tool using Fire and Rich for
interactive HTML content extraction and merging.
"""

import sys
from pathlib import Path
from typing import Optional, Union

import fire
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from htmladapt import HTMLExtractMergeTool, ProcessingConfig, LLMReconciler
from htmladapt.__version__ import __version__


class HTMLAdaptCLI:
    """HTMLAdapt command-line interface."""

    def __init__(self) -> None:
        self.console = Console()

    def version(self) -> None:
        """Display version information."""
        self.console.print(f"HTMLAdapt v{__version__}")

    def extract(
        self,
        full_path: str | Path,
        map_path: str | Path | None = None,
        comp_path: str | Path | None = None,
        id_prefix: str = "xhq",
        perf: str = "balanced",
    ) -> None:
        """Extract content from HTML file into map_path and subset documents.

        Args:
            full_path: Path to old_path HTML file
            map_path: Path for 'map_path' map HTML new_path (optional)
            comp_path: Path for comp HTML new_path (optional)
            id_prefix: Prefix for generated IDs (default: "xhq")
            perf: Performance profile - fast|balanced|accurate (default: "balanced")
        """
        full_path = Path(full_path)

        if not full_path.exists():
            self.console.print(f"[red]Error: Input file {full_path} not found[/red]")
            sys.exit(1)

        # Set default new_path paths if not provided
        if map_path is None:
            map_path = full_path.with_suffix(".m.html")
        if comp_path is None:
            comp_path = full_path.with_suffix(".c.html")

        map_path = Path(map_path)
        comp_path = Path(comp_path)

        # Create configuration
        config = ProcessingConfig(id_prefix=id_prefix, perf=perf)

        # Initialize tool
        tool = HTMLExtractMergeTool(config=config)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            # Read input file
            task = progress.add_task("Reading input file...", total=None)
            try:
                html_content = full_path.read_text(encoding="utf-8")
                progress.update(task, description="Processing HTML...")

                # Extract content
                map_html, comp_html = tool.extract(html_content)

                # Write new_path files
                progress.update(task, description="Writing new_path files...")
                map_path.write_text(map_html, encoding="utf-8")
                comp_path.write_text(comp_html, encoding="utf-8")

                progress.update(task, description="Extraction complete!")

            except Exception as e:
                self.console.print(f"[red]Error during extraction: {e}[/red]")
                sys.exit(1)

        # Display results
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File Type")
        table.add_column("Path")
        table.add_column("Size")

        table.add_row("old", str(full_path), f"{full_path.stat().st_size} bytes")
        table.add_row("map", str(map_path), f"{map_path.stat().st_size} bytes")
        table.add_row("comp", str(comp_path), f"{comp_path.stat().st_size} bytes")

        self.console.print("\n[green]✅ Extraction completed successfully![/green]")
        self.console.print(table)

    def merge(
        self,
        cnew_path: str | Path,
        Cold_path: str | Path,
        map_path: str | Path,
        old_path: str | Path,
        new_path: str | Path | None = None,
        id_prefix: str = "xhq",
        simi_level: float = 0.7,
        llm_use: bool = False,
        model_llm: str = "gpt-4o-mini",
        perf: str = "balanced",
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
            llm_use: Use LLM for conflict resolution (default: False)
            model_llm: LLM model name (default: "gpt-4o-mini")
            perf: Performance profile - fast|balanced|accurate (default: "balanced")
        """
        cnew_path = Path(cnew_path)
        cold_path = Path(Cold_path)
        map_path = Path(map_path)
        old_path = Path(old_path)

        # Check all input files exist
        for path in [cnew_path, cold_path, map_path, old_path]:
            if not path.exists():
                self.console.print(f"[red]Error: Input file {path} not found[/red]")
                sys.exit(1)

        # Set default new_path path if not provided
        if new_path is None:
            new_path = old_path.with_suffix(".n.html")
        new_path = Path(new_path)

        # Create configuration
        config = ProcessingConfig(
            id_prefix=id_prefix,
            simi_level=simi_level,
            llm_use=llm_use,
            model_llm=model_llm,
            perf=perf,
        )

        # Initialize LLM reconciler if enabled
        llm_reconciler = None
        if llm_use:
            try:
                import os

                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    self.console.print(
                        "[red]Error: OPENAI_API_KEY environment variable required for LLM resolution[/red]"
                    )
                    sys.exit(1)
                llm_reconciler = LLMReconciler(api_key=api_key, model=model_llm)
            except ImportError:
                self.console.print(
                    "[red]Error: OpenAI dependencies not installed. Use 'pip install htmladapt[llm]'[/red]"
                )
                sys.exit(1)

        # Initialize tool
        tool = HTMLExtractMergeTool(config=config, llm_reconciler=llm_reconciler)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Reading input files...", total=None)
            try:
                # Read all input files
                cnew_html = cnew_path.read_text(encoding="utf-8")
                cold_html = cold_path.read_text(encoding="utf-8")
                map_html = map_path.read_text(encoding="utf-8")
                old_html = old_path.read_text(encoding="utf-8")

                progress.update(task, description="Merging content...")

                # Merge content
                new_html = tool.merge(cnew_html, cold_html, map_html, old_html)

                progress.update(task, description="Writing new_path file...")
                new_path.write_text(new_html, encoding="utf-8")

                progress.update(task, description="Merge complete!")

            except Exception as e:
                self.console.print(f"[red]Error during merge: {e}[/red]")
                sys.exit(1)

        # Display results
        self.console.print(f"\n[green]✅ Merge completed successfully![/green]")
        self.console.print(f"new_path written to: [cyan]{new_path}[/cyan]")
        self.console.print(f"new_path size: {new_path.stat().st_size} bytes")


def main() -> None:
    """Main CLI entry point."""
    try:
        fire.Fire(HTMLAdaptCLI)
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
