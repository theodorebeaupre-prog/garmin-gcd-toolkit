"""CLI entry point for gcd-tool."""

import click
from rich.console import Console

console = Console()

GCD_MAGIC = b"GARMINd\x00"


@click.group()
@click.version_option()
def main() -> None:
    """Garmin .GCD firmware toolkit — parse, list, and extract resources."""


@main.command()
@click.argument("gcd_file", type=click.Path(exists=True, dir_okay=False))
def inspect(gcd_file: str) -> None:
    """Show header fields and file metadata."""
    with open(gcd_file, "rb") as f:
        magic = f.read(8)
    if magic != GCD_MAGIC:
        console.print(f"[red]ERROR:[/red] Not a GCD file (magic mismatch: {magic!r})")
        raise SystemExit(1)
    console.print(f"[green]✓[/green] Magic: {magic[:7].decode()} (valid)")
    console.print("[yellow]Header parsing not yet implemented — coming in Phase 2.[/yellow]")


@main.command("list")
@click.argument("gcd_file", type=click.Path(exists=True, dir_okay=False))
def list_sections(gcd_file: str) -> None:
    """List all sections / records in the GCD file."""
    console.print("[yellow]Section listing not yet implemented — coming in Phase 3.[/yellow]")


@main.command()
@click.argument("gcd_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--output", "-o", default="./output", show_default=True,
              help="Output directory for extracted resources.")
def extract(gcd_file: str, output: str) -> None:
    """Extract embedded resources (PNG, gzip, etc.) from a GCD file."""
    console.print("[yellow]Extraction not yet implemented — coming in Phase 4.[/yellow]")
