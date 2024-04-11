import click

from cuda_redist_find_features.cmd._types import VERSION_PARAM_TYPE, NoneOrVersion


def _max_version_option_callback(
    ctx: click.Context, param: click.Parameter, max_version: NoneOrVersion
) -> NoneOrVersion:
    if max_version is not None:
        if ctx.params.get("version") is not None:
            raise click.BadParameter("Cannot specify both --max-version and --version.")
        if ctx.params.get("min_version") is not None and max_version < ctx.params["min_version"]:
            raise click.BadParameter("--max-version cannot be less than --min-version.")
        click.echo(f"Maximum version set to {max_version}.")
    return max_version


max_version_option = click.option(
    "--max-version",
    type=VERSION_PARAM_TYPE,
    default=None,
    help="Maximum version to accept. Exclusive with --version.",
    callback=_max_version_option_callback,
)
