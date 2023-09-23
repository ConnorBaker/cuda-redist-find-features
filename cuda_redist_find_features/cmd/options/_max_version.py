import logging

import click

from ..types import VERSION_OPTION, NoneOrVersion


def _max_version_callback(ctx: click.Context, param: click.Parameter, max_version: NoneOrVersion) -> NoneOrVersion:
    if max_version is not None:
        if ctx.params.get("version") is not None:
            raise click.BadParameter("Cannot specify both --max-version and --version.")
        if ctx.params.get("min_version") is not None and max_version < ctx.params["min_version"]:
            raise click.BadParameter("--max-version cannot be less than --min-version.")
        logging.info(f"Maximum version set to {max_version}.")
    return max_version


max_version = click.option(
    "--max-version",
    type=VERSION_OPTION,
    default=None,
    help="Maximum version to accept. Exclusive with --version.",
    callback=_max_version_callback,
)
