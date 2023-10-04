import pathlib

import click


def _overrides_json_argument_callback(
    ctx: click.Context, param: click.Parameter, overrides_json: pathlib.Path
) -> pathlib.Path:
    click.echo(f"Using overrides JSON file {overrides_json}")
    return overrides_json


overrides_json_argument = click.argument(
    "overrides_json",
    type=click.Path(
        path_type=pathlib.Path,
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=True,
        resolve_path=True,
    ),
    callback=_overrides_json_argument_callback,
)
