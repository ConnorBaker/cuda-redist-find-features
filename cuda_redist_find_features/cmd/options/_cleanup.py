import logging

import click


def _cleanup_callback(ctx: click.Context, param: click.Parameter, cleanup: bool) -> bool:
    if cleanup:
        logging.info("Removing files after use.")
    return cleanup


cleanup = click.option(
    "--cleanup/--no-cleanup",
    type=bool,
    default=False,
    help="Remove files after use.",
    show_default=True,
    callback=_cleanup_callback,
)
