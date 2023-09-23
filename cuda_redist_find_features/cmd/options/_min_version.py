import logging

import click

from ..types import VERSION_OPTION, NoneOrVersion


def _min_version_callback(ctx: click.Context, param: click.Parameter, min_version: NoneOrVersion) -> NoneOrVersion:
    if min_version is not None:
        if ctx.params.get("version") is not None:
            raise click.BadParameter("Cannot specify both --min-version and --version.")
        if ctx.params.get("max_version") is not None and min_version > ctx.params["max_version"]:
            raise click.BadParameter("--min-version cannot be greater than --max-version.")
        logging.info(f"Minimum version set to {min_version}.")
    return min_version


min_version = click.option(
    "--min-version",
    type=VERSION_OPTION,
    default=None,
    help="Minimum version to accept. Exclusive with --version.",
    callback=_min_version_callback,
)
