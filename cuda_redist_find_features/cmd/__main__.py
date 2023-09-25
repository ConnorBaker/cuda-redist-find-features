import click

from . import option


@click.group()
@option.debug_option
def main(debug: bool) -> None:
    return
