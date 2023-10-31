from pathlib import Path

import click
from pydantic import HttpUrl

from cuda_redist_find_features.types import LogLevel, Version, VersionConstraint

from .argument import manifest_dir_argument, url_argument
from .option import (
    cleanup_option,
    log_level_option,
    max_version_option,
    min_version_option,
    no_parallel_option,
    version_option,
)


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
    from .download_manifests_impl import download_manifests_impl

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
# @overrides_json_argument
@log_level_option
@cleanup_option
@no_parallel_option
@min_version_option
@max_version_option
@version_option
def process_manifests(
    url: HttpUrl,
    manifest_dir: Path,
    # overrides_json: Path,
    log_level: LogLevel,
    cleanup: bool,
    no_parallel: bool,
    min_version: None | Version,
    max_version: None | Version,
    version: None | Version,
) -> None:
    # Lazily import so our callback on log_level sets the logging level first.
    from .process_manifests_impl import process_manifests_impl

    # Create the version constraint
    version_constraint = VersionConstraint(
        version_min=min_version,
        version_max=max_version,
        version=version,
    )
    process_manifests_impl(
        url=url,
        manifest_dir=manifest_dir,
        # overrides_json=overrides_json,
        cleanup=cleanup,
        no_parallel=no_parallel,
        version_constraint=version_constraint,
    )


@main.command()
def print_manifest_schema() -> None:
    import json

    from cuda_redist_find_features.manifest.nvidia import NvidiaManifest

    print(json.dumps(NvidiaManifest.model_json_schema(), indent=2))


@main.command()
def print_feature_schema() -> None:
    import json

    from cuda_redist_find_features.manifest.feature import FeatureManifest

    print(json.dumps(FeatureManifest.model_json_schema(), indent=2))
