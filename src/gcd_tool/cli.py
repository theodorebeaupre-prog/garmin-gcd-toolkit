"""CLI entry point for gcd-tool."""

import click
from rich.console import Console
from rich.table import Table

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
@click.option("--limit", "-n", default=20, help="Max records to show.")
def list_sections(gcd_file: str, limit: int) -> None:
    """List records in the GCD file."""
    from gcd_tool.walker import walk_file

    records = walk_file(gcd_file)
    table = Table(title=f"GCD Records: {gcd_file}")
    table.add_column("Offset", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("FieldA")
    table.add_column("FieldB")
    table.add_column("Payload size", justify="right")
    for rec in records[:limit]:
        table.add_row(
            hex(rec.offset),
            f"0x{rec.type:02x}",
            rec.field_a.hex(),
            rec.field_b.hex(),
            str(rec.payload_size),
        )
    console.print(table)
    console.print(f"Showing {min(limit, len(records))} of {len(records)} records.")


@main.command()
@click.argument("gcd_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--output", "-o", default="./output", show_default=True,
              help="Output directory for extracted resources.")
def extract(gcd_file: str, output: str) -> None:
    """Extract embedded resources (PNG, gzip, etc.) from a GCD file."""
    console.print("[yellow]Extraction not yet implemented — coming in Phase 4.[/yellow]")
