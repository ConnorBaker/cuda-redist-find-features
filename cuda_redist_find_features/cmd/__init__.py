from pathlib import Path

import click
from pydantic import HttpUrl

from cuda_redist_find_features.cmd.argument import manifest_dir_argument, url_argument
from cuda_redist_find_features.cmd.option import (
    cleanup_option,
    log_level_option,
    max_version_option,
    min_version_option,
    no_parallel_option,
    version_option,
)
from cuda_redist_find_features.types import LogLevel
from cuda_redist_find_features.version import Version
from cuda_redist_find_features.version_constraint import VersionConstraint


@click.group()
def main() -> None:
    return


@main.command()
@url_argument
@manifest_dir_argument(file_okay=False, dir_okay=True)
@log_level_option
@no_parallel_option
@min_version_option
@max_version_option
@version_option
def download_manifests(
    url: HttpUrl,
    manifest_dir: Path,
    log_level: LogLevel,
    no_parallel: bool,
    min_version: None | Version,
    max_version: None | Version,
    version: None | Version,
) -> None:
    # Lazily import so our callback on log_level sets the logging level first.
    from cuda_redist_find_features.cmd.download_manifests_impl import download_manifests_impl

    # Create the version constraint
    version_constraint = VersionConstraint(
        version_min=min_version,
        version_max=max_version,
        version=version,
    )
    download_manifests_impl(
        url=url,
        manifest_dir=manifest_dir,
        no_parallel=no_parallel,
        version_constraint=version_constraint,
    )


@main.command()
@url_argument
@manifest_dir_argument(file_okay=False, dir_okay=True)
@log_level_option
@cleanup_option
@no_parallel_option
@min_version_option
@max_version_option
@version_option
def process_manifests(
    url: HttpUrl,
    manifest_dir: Path,
    log_level: LogLevel,
    cleanup: bool,
    no_parallel: bool,
    min_version: None | Version,
    max_version: None | Version,
    version: None | Version,
) -> None:
    # Lazily import so our callback on log_level sets the logging level first.
    from cuda_redist_find_features.cmd.process_manifests_impl import process_manifests_impl

    # Create the version constraint
    version_constraint = VersionConstraint(
        version_min=min_version,
        version_max=max_version,
        version=version,
    )
    process_manifests_impl(
        url=url,
        manifest_dir=manifest_dir,
        cleanup=cleanup,
        no_parallel=no_parallel,
        version_constraint=version_constraint,
    )
