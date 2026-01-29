"""CLI entry point for LandingForge."""

import asyncio
import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import __version__
from .models import DesignAnalysis, ProductInfo, Feature
from .scraper import scrape_landing_pages
from .analyzer import analyze_designs
from .generator import generate_landing_page

console = Console()


@click.group()
@click.version_option(version=__version__)
def main():
    """LandingForge - AI-powered landing page generator.

    Analyze beautiful landing pages and generate custom pages inspired by their design.
    """
    pass


@main.command()
@click.argument("urls", nargs=-1, required=True)
@click.option("--output", "-o", type=click.Path(), help="Output JSON file for analysis")
def analyze(urls: tuple[str, ...], output: str | None):
    """Analyze landing pages and extract design patterns.

    URLS: One or more landing page URLs to analyze (max 5)
    """
    if len(urls) > 5:
        console.print("[red]Error: Maximum 5 URLs allowed[/red]")
        sys.exit(1)

    # Normalize URLs
    normalized_urls = []
    for url in urls:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        normalized_urls.append(url)

    async def run_analysis():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Scraping URLs...", total=None)
            scraped = await scrape_landing_pages(normalized_urls)

            progress.update(task, description="Analyzing design patterns...")
            analysis = analyze_designs(scraped)

            return analysis

    analysis = asyncio.run(run_analysis())

    # Display results
    console.print()
    console.print(Panel.fit("[bold green]Design Analysis Complete[/bold green]"))
    console.print()

    # Colors table
    colors_table = Table(title="Color Palette")
    colors_table.add_column("Role", style="cyan")
    colors_table.add_column("Color", style="magenta")
    colors_table.add_row("Primary", analysis.colors.primary)
    colors_table.add_row("Secondary", analysis.colors.secondary)
    colors_table.add_row("Accent", analysis.colors.accent)
    colors_table.add_row("Background", analysis.colors.background)
    colors_table.add_row("Text", analysis.colors.text)
    console.print(colors_table)
    console.print()

    # Typography
    console.print(f"[bold]Typography:[/bold]")
    console.print(f"  Heading Font: {analysis.typography.heading_font}")
    console.print(f"  Body Font: {analysis.typography.body_font}")
    console.print()

    # Sections
    console.print(f"[bold]Detected Sections:[/bold] {', '.join(analysis.sections)}")
    console.print(f"[bold]Dark Mode:[/bold] {'Yes' if analysis.layout.is_dark_mode else 'No'}")
    console.print()

    # Save to file if requested
    if output:
        output_path = Path(output)
        with open(output_path, "w") as f:
            json.dump(analysis.model_dump(), f, indent=2)
        console.print(f"[green]Analysis saved to {output_path}[/green]")


@main.command()
@click.option("--name", "-n", required=True, help="Product/company name")
@click.option("--tagline", "-t", required=True, help="Hero headline/tagline")
@click.option("--description", "-d", default="", help="Product description")
@click.option("--feature", "-f", multiple=True, help="Feature in format 'Title:Description'")
@click.option("--cta-text", default="Get Started", help="CTA button text")
@click.option("--cta-url", default="#", help="CTA button URL")
@click.option("--analysis", "-a", type=click.Path(exists=True), help="JSON file with design analysis")
@click.option("--output", "-o", type=click.Path(), default="landing-page.html", help="Output HTML file")
@click.option("--dark", is_flag=True, help="Use dark mode design")
def generate(
    name: str,
    tagline: str,
    description: str,
    feature: tuple[str, ...],
    cta_text: str,
    cta_url: str,
    analysis: str | None,
    output: str,
    dark: bool,
):
    """Generate a landing page from product info.

    Use with --analysis to apply design patterns from analyzed sites,
    or generate with default styling.
    """
    # Parse features
    features = []
    for f in feature:
        if ":" in f:
            title, desc = f.split(":", 1)
            features.append(Feature(title=title.strip(), description=desc.strip()))
        else:
            features.append(Feature(title=f, description=""))

    product = ProductInfo(
        name=name,
        tagline=tagline,
        description=description,
        features=features,
        cta_text=cta_text,
        cta_url=cta_url,
    )

    # Load or create design analysis
    if analysis:
        with open(analysis) as f:
            design_data = json.load(f)
            design = DesignAnalysis.model_validate(design_data)
    else:
        # Default design
        from .models import ColorPalette, Typography, LayoutPattern

        if dark:
            colors = ColorPalette(
                primary="#6366f1",
                secondary="#4f46e5",
                accent="#f59e0b",
                background="#0f172a",
                text="#f8fafc",
            )
        else:
            colors = ColorPalette(
                primary="#3b82f6",
                secondary="#1e40af",
                accent="#f59e0b",
                background="#ffffff",
                text="#1f2937",
            )

        design = DesignAnalysis(
            colors=colors,
            typography=Typography(),
            layout=LayoutPattern(is_dark_mode=dark),
            sections=["hero", "features", "cta", "footer"],
            animations=[],
            source_urls=[],
        )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating landing page with AI...", total=None)
        result = generate_landing_page(design, product)

    # Save output
    output_path = Path(output)
    with open(output_path, "w") as f:
        f.write(result.html)

    console.print()
    console.print(Panel.fit(f"[bold green]Landing page generated![/bold green]\n\nSaved to: {output_path}"))
    console.print()
    console.print("Open the file in a browser to preview your landing page.")


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", "-p", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def serve(host: str, port: int, reload: bool):
    """Start the LandingForge API server."""
    console.print(f"[bold green]Starting LandingForge API server[/bold green]")
    console.print(f"  URL: http://{host}:{port}")
    console.print(f"  Docs: http://{host}:{port}/docs")
    console.print()

    from .api import run_server
    run_server(host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()
