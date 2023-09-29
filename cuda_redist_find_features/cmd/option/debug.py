import logging

import click
from rich.logging import RichHandler


def _debug_option_callback(ctx: click.Context, param: click.Parameter, debug: bool) -> bool:
    if debug and logging.root.level == logging.DEBUG:
        logging.warning("Debug logging already enabled; perhaps you specified --debug twice?")
        return debug

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="[PID%(process)s][%(funcName)s] %(message)s",
        # Use ISO8601 format for the timestamp
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        handlers=[RichHandler()],
    )
    if debug:
        logging.debug("Debug logging enabled.")
    return debug


debug_option = click.option(
    "--debug/--no-debug",
    type=bool,
    default=False,
    help="Enable debug logging.",
    show_default=True,
    callback=_debug_option_callback,
)
