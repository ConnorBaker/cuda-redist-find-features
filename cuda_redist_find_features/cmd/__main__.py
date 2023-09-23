import click

from . import options


@click.group()
@options.debug
def main(debug: bool) -> None:
    return
