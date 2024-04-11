import logging

import click

from cuda_redist_find_features import utilities
from cuda_redist_find_features._types import LogLevel, LogLevels


def _log_level_callback(ctx: click.Context, param: click.Parameter, log_level: LogLevel) -> LogLevel:
    utilities.LOGGING_LEVEL = getattr(logging, log_level)
    click.echo(f"Set logging level to {log_level}.")
    return log_level


log_level_option = click.option(
    "--log-level",
    type=click.Choice(LogLevels),
    default="WARNING",
    help="Set the logging level.",
    show_default=True,
    callback=_log_level_callback,
)
