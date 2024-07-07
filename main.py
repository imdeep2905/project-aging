import click
from src.raw_converter.main import main as raw_converter_main


@click.group()
def cli():
    """CLI tool for Project Aging."""
    pass


@cli.command()
@click.option(
    "--dir", default="in/raw_imgs", help="Input directory containing raw images."
)
@click.option(
    "--default_tz",
    default="America/Toronto",
    help="Default timezone in case no timezone is found for any image.",
)
def raw_convert(dir, default_tz):
    """Convert raw images in the specified directory"""
    raw_converter_main(dir, default_tz)


if __name__ == "__main__":
    cli()
