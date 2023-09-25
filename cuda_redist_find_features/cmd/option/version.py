import json
import logging

import click

from ..types import VERSION_PARAM_TYPE, NoneOrVersion


def _version_option_callback(ctx: click.Context, param: click.Parameter, version: NoneOrVersion) -> NoneOrVersion:
    if version is not None:
        logging.info(json.dumps(ctx.params))
        if ctx.params.get("min_version") is not None:
            raise click.BadParameter("Cannot specify both --version and --min-version.")
        if ctx.params.get("max_version") is not None:
            raise click.BadParameter("Cannot specify both --version and --max-version.")
        logging.info(f"Version set to {version}.")
    return version


version_option = click.option(
    "--version",
    type=VERSION_PARAM_TYPE,
    default=None,
    help=" ".join(
        [
            "Version to accept.",
            "If not specified, operates on all versions.",
            "Exclusive with --min-version and --max-version.",
        ]
    ),
    callback=_version_option_callback,
)
