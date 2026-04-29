"""CLI for atl08_lines"""

from pathlib import Path

import click

from atl08_lines.read_geom import lines_from_atl08_points, read_points_from_atl08


@click.group()  # type: ignore[untyped-decorator]
def cli() -> None:
    pass


@cli.command()  # type: ignore[untyped-decorator]
@click.argument("input_filepath", required=True, type=click.Path())  # type: ignore[untyped-decorator]
@click.argument("output_filepath", required=True, type=click.Path())  # type: ignore[untyped-decorator]
def atl08_to_points(input_filepath: Path, output_filepath: Path) -> None:
    """Given an ATL08 hdf5 as input, output a file with point geometries."""
    points = read_points_from_atl08(filepath=input_filepath)

    points.to_file(output_filepath)


@cli.command()  # type: ignore[untyped-decorator]
@click.argument("input_filepath", required=True, type=click.Path())  # type: ignore[untyped-decorator]
@click.argument("output_filepath", required=True, type=click.Path())  # type: ignore[untyped-decorator]
@click.option(
    "--gap-threshold-meters",
    default=500,
    type=int,
    help="Length, in meters, between consecutive points that when exceeded should be considered a 'gap' and produce a new line segment.",
)  # type: ignore[untyped-decorator]
def atl08_to_lines(
    input_filepath: Path, output_filepath: Path, gap_threshold_meters: int
) -> None:
    """Given an ATL08 hdf5 as input, output a file with line geometries."""
    points = read_points_from_atl08(filepath=input_filepath)

    lines = lines_from_atl08_points(
        points=points,
        gap_threshold_meters=gap_threshold_meters,
    )

    lines.to_file(output_filepath)


if __name__ == "__main__":
    cli()
