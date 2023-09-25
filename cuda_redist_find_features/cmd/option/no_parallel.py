import logging

import click


def _no_parallel_option_callback(ctx: click.Context, param: click.Parameter, no_parallel: bool) -> bool:
    if no_parallel:
        logging.debug("Parallel processing disabled.")
    return no_parallel


no_parallel_option = click.option(
    "--no-parallel/--parallel",
    type=bool,
    default=False,
    help="Disable parallel processing.",
    show_default=True,
    callback=_no_parallel_option_callback,
)
