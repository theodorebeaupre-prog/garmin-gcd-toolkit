"""CLI entry point for gcd-tool."""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

console = Console()

GCD_MAGIC = b"GARMINd\x00"


def _parse_type_filter(type_value: str | None) -> set[int] | None:
    if type_value is None:
        return None
    values = [part.strip() for part in type_value.split(",") if part.strip()]
    parsed: set[int] = set()
    for value in values:
        parsed.add(int(value, 0))
    return parsed


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
@click.option(
    "--type",
    "type_filter",
    default=None,
    help="Comma-separated record type filter, e.g. 0x64,0x03",
)
def extract(gcd_file: str, output: str, type_filter: str | None) -> None:
    """Extract embedded resources (PNG, gzip, etc.) from a GCD file."""
    from gcd_tool.extractor import extract_resources

    summary = extract_resources(
        gcd_file,
        Path(output),
        type_filter=_parse_type_filter(type_filter),
    )
    table = Table(title=f"Extracted resources: {gcd_file}")
    table.add_column("Kind", style="magenta")
    table.add_column("Record", style="cyan")
    table.add_column("Offset", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("MIME")
    table.add_column("Path")
    for resource in summary.resources:
        table.add_row(
            resource.kind,
            f"0x{resource.record_type:02x}@0x{resource.record_offset:x}",
            hex(resource.absolute_offset),
            str(resource.size),
            resource.detected_mime,
            str(resource.path),
        )
    console.print(table)
    console.print(
        f"Extracted {len(summary.resources)} resources "
        f"({summary.png_count} PNG, {summary.gzip_count} gzip-signature hits)."
    )


@main.command()
@click.argument("gcd_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--type", "record_type", default="0x01", help="Record type to analyze")
@click.option("--output", "-o", default="./analysis/", help="Output directory placeholder.")
def analyze(gcd_path: str, record_type: str, output: str) -> None:
    """Analyze specific record types for classification."""
    from gcd_tool.analyzer import analyze_record_type

    parsed_type = int(record_type, 0)
    analyses = analyze_record_type(gcd_path, parsed_type)

    table = Table(title=f"Analysis: {gcd_path} type 0x{parsed_type:02x}")
    table.add_column("Record", style="cyan")
    table.add_column("Class", style="magenta")
    table.add_column("Confidence", justify="right")
    table.add_column("Payload size", justify="right")
    table.add_column("Details")
    for item in analyses:
        table.add_row(
            hex(int(item["record_offset"])),
            str(item["type"]),
            f"{float(item['confidence']):.2f}",
            str(int(item["payload_size"])),
            str(item["details"]),
        )
    console.print(table)
    console.print(f"Analysis output directory reserved: {output}")
