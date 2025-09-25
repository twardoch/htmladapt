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
        input_file: str | Path,
        superset_output: str | Path | None = None,
        subset_output: str | Path | None = None,
        id_prefix: str = "auto_",
        performance_profile: str = "balanced"
    ) -> None:
        """Extract content from HTML file into superset and subset documents.

        Args:
            input_file: Path to input HTML file
            superset_output: Path for superset HTML output (optional)
            subset_output: Path for subset HTML output (optional)
            id_prefix: Prefix for generated IDs (default: "auto_")
            performance_profile: Performance profile - fast|balanced|accurate (default: "balanced")
        """
        input_path = Path(input_file)

        if not input_path.exists():
            self.console.print(f"[red]Error: Input file {input_path} not found[/red]")
            sys.exit(1)

        # Set default output paths if not provided
        if superset_output is None:
            superset_output = input_path.with_suffix('.superset.html')
        if subset_output is None:
            subset_output = input_path.with_suffix('.subset.html')

        superset_path = Path(superset_output)
        subset_path = Path(subset_output)

        # Create configuration
        config = ProcessingConfig(
            id_prefix=id_prefix,
            performance_profile=performance_profile
        )

        # Initialize tool
        tool = HTMLExtractMergeTool(config=config)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:

            # Read input file
            task = progress.add_task("Reading input file...", total=None)
            try:
                html_content = input_path.read_text(encoding='utf-8')
                progress.update(task, description="Processing HTML...")

                # Extract content
                superset_html, subset_html = tool.extract(html_content)

                # Write output files
                progress.update(task, description="Writing output files...")
                superset_path.write_text(superset_html, encoding='utf-8')
                subset_path.write_text(subset_html, encoding='utf-8')

                progress.update(task, description="Extraction complete!")

            except Exception as e:
                self.console.print(f"[red]Error during extraction: {e}[/red]")
                sys.exit(1)

        # Display results
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File Type")
        table.add_column("Path")
        table.add_column("Size")

        table.add_row("Original", str(input_path), f"{input_path.stat().st_size} bytes")
        table.add_row("Superset", str(superset_path), f"{superset_path.stat().st_size} bytes")
        table.add_row("Subset", str(subset_path), f"{subset_path.stat().st_size} bytes")

        self.console.print("\n[green]✅ Extraction completed successfully![/green]")
        self.console.print(table)

    def merge(
        self,
        edited_subset: str | Path,
        original_subset: str | Path,
        superset: str | Path,
        original: str | Path,
        output: str | Path | None = None,
        id_prefix: str = "auto_",
        similarity_threshold: float = 0.7,
        enable_llm: bool = False,
        llm_model: str = "gpt-4o-mini",
        performance_profile: str = "balanced"
    ) -> None:
        """Merge edited content back into original HTML structure.

        Args:
            edited_subset: Path to edited subset HTML file
            original_subset: Path to original subset HTML file
            superset: Path to superset HTML file
            original: Path to original HTML file
            output: Path for merged output (optional)
            id_prefix: Prefix for generated IDs (default: "auto_")
            similarity_threshold: Minimum similarity for fuzzy matching (default: 0.7)
            enable_llm: Use LLM for conflict resolution (default: False)
            llm_model: LLM model name (default: "gpt-4o-mini")
            performance_profile: Performance profile - fast|balanced|accurate (default: "balanced")
        """
        edited_path = Path(edited_subset)
        original_subset_path = Path(original_subset)
        superset_path = Path(superset)
        original_path = Path(original)

        # Check all input files exist
        for path in [edited_path, original_subset_path, superset_path, original_path]:
            if not path.exists():
                self.console.print(f"[red]Error: Input file {path} not found[/red]")
                sys.exit(1)

        # Set default output path if not provided
        if output is None:
            output = original_path.with_suffix('.merged.html')
        output_path = Path(output)

        # Create configuration
        config = ProcessingConfig(
            id_prefix=id_prefix,
            similarity_threshold=similarity_threshold,
            enable_llm_resolution=enable_llm,
            llm_model=llm_model,
            performance_profile=performance_profile
        )

        # Initialize LLM reconciler if enabled
        llm_reconciler = None
        if enable_llm:
            try:
                import os
                api_key = os.environ.get('OPENAI_API_KEY')
                if not api_key:
                    self.console.print("[red]Error: OPENAI_API_KEY environment variable required for LLM resolution[/red]")
                    sys.exit(1)
                llm_reconciler = LLMReconciler(api_key=api_key, model=llm_model)
            except ImportError:
                self.console.print("[red]Error: OpenAI dependencies not installed. Use 'pip install htmladapt[llm]'[/red]")
                sys.exit(1)

        # Initialize tool
        tool = HTMLExtractMergeTool(config=config, llm_reconciler=llm_reconciler)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:

            task = progress.add_task("Reading input files...", total=None)
            try:
                # Read all input files
                edited_html = edited_path.read_text(encoding='utf-8')
                original_subset_html = original_subset_path.read_text(encoding='utf-8')
                superset_html = superset_path.read_text(encoding='utf-8')
                original_html = original_path.read_text(encoding='utf-8')

                progress.update(task, description="Merging content...")

                # Merge content
                merged_html = tool.merge(
                    edited_html,
                    original_subset_html,
                    superset_html,
                    original_html
                )

                progress.update(task, description="Writing output file...")
                output_path.write_text(merged_html, encoding='utf-8')

                progress.update(task, description="Merge complete!")

            except Exception as e:
                self.console.print(f"[red]Error during merge: {e}[/red]")
                sys.exit(1)

        # Display results
        self.console.print(f"\n[green]✅ Merge completed successfully![/green]")
        self.console.print(f"Output written to: [cyan]{output_path}[/cyan]")
        self.console.print(f"Output size: {output_path.stat().st_size} bytes")

    def process(
        self,
        input_file: str | Path,
        output_file: str | Path | None = None,
        id_prefix: str = "auto_",
        similarity_threshold: float = 0.7,
        enable_llm: bool = False,
        llm_model: str = "gpt-4o-mini",
        performance_profile: str = "balanced",
        keep_intermediates: bool = False
    ) -> None:
        """Full extract-edit-merge workflow with external editor.

        Args:
            input_file: Path to input HTML file
            output_file: Path for final output (optional)
            id_prefix: Prefix for generated IDs (default: "auto_")
            similarity_threshold: Minimum similarity for fuzzy matching (default: 0.7)
            enable_llm: Use LLM for conflict resolution (default: False)
            llm_model: LLM model name (default: "gpt-4o-mini")
            performance_profile: Performance profile - fast|balanced|accurate (default: "balanced")
            keep_intermediates: Keep intermediate files after processing (default: False)
        """
        input_path = Path(input_file)

        if not input_path.exists():
            self.console.print(f"[red]Error: Input file {input_path} not found[/red]")
            sys.exit(1)

        # Set default output path if not provided
        if output_file is None:
            output_file = input_path.with_suffix('.processed.html')
        output_path = Path(output_file)

        # Create intermediate file paths
        superset_path = input_path.with_suffix('.superset.html')
        subset_path = input_path.with_suffix('.subset.html')

        # Step 1: Extract
        self.console.print("[bold blue]Step 1: Extracting content...[/bold blue]")
        self.extract(
            input_file=input_path,
            superset_output=superset_path,
            subset_output=subset_path,
            id_prefix=id_prefix,
            performance_profile=performance_profile
        )

        # Step 2: Prompt for editing
        self.console.print(f"\n[bold yellow]Step 2: Edit the subset file:[/bold yellow]")
        self.console.print(Panel(
            f"Please edit the content in: {subset_path}\n\n"
            "This file contains only the translatable/editable content.\n"
            "Make your changes and save the file, then press Enter to continue...",
            title="Manual Editing Required",
            border_style="yellow"
        ))
        input("Press Enter when you've finished editing...")

        # Step 3: Merge
        self.console.print("\n[bold blue]Step 3: Merging edited content...[/bold blue]")
        self.merge(
            edited_subset=subset_path,
            original_subset=subset_path,  # Note: using same file as both edited and original
            superset=superset_path,
            original=input_path,
            output=output_path,
            id_prefix=id_prefix,
            similarity_threshold=similarity_threshold,
            enable_llm=enable_llm,
            llm_model=llm_model,
            performance_profile=performance_profile
        )

        # Cleanup intermediate files if requested
        if not keep_intermediates:
            try:
                superset_path.unlink()
                subset_path.unlink()
                self.console.print("[dim]Cleaned up intermediate files[/dim]")
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not clean up intermediate files: {e}[/yellow]")

        self.console.print(f"\n[green]🎉 Process completed! Final output: {output_path}[/green]")


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