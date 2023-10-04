import click


def _cleanup_option_callback(ctx: click.Context, param: click.Parameter, cleanup: bool) -> bool:
    if cleanup:
        click.echo("Removing files after use.")
    return cleanup


cleanup_option = click.option(
    "--cleanup/--no-cleanup",
    type=bool,
    default=False,
    help="Remove files after use.",
    show_default=True,
    callback=_cleanup_option_callback,
)
