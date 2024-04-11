import click

from cuda_redist_find_features._types import RedistName, RedistNames


def _redist_option_callback(ctx: click.Context, param: click.Parameter, redist: RedistName) -> RedistName:
    click.echo(f"Requested redist: {redist}.")
    return redist


redist_option = click.option(
    "--redist",
    type=click.Choice(RedistNames),
    help="Redistributable to select.",
    callback=_redist_option_callback,
    required=True,
)
