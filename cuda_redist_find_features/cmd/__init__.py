import click

from cuda_redist_find_features._types import LogLevel, RedistName, Version, VersionConstraint

from .option import (
    cleanup_option,
    log_level_option,
    max_version_option,
    min_version_option,
    no_parallel_option,
    redist_option,
    version_option,
)


@click.group()
def main() -> None:
    return


@main.command()
@redist_option
@log_level_option
@no_parallel_option
@min_version_option
@max_version_option
@version_option
def download_manifests(  # noqa: PLR0917
    redist: RedistName,
    log_level: LogLevel,
    no_parallel: bool,
    min_version: None | Version,
    max_version: None | Version,
    version: None | Version,
) -> None:
    """
    Downloads manifest files belonging to REDIST to ./redistrib_manifests/REDIST.
    """

    # Lazily import so our callback on log_level sets the logging level first.
    from .download_manifests_impl import download_manifests_impl  # noqa: PLC0415

    # Create the version constraint
    version_constraint = VersionConstraint(
        version_min=min_version,
        version_max=max_version,
        version=version,
    )
    download_manifests_impl(
        redist=redist,
        no_parallel=no_parallel,
        version_constraint=version_constraint,
    )


@main.command()
@redist_option
@log_level_option
@cleanup_option
@no_parallel_option
@min_version_option
@max_version_option
@version_option
def process_manifests(  # noqa: PLR0917
    redist: RedistName,
    log_level: LogLevel,
    cleanup: bool,
    no_parallel: bool,
    min_version: None | Version,
    max_version: None | Version,
    version: None | Version,
) -> None:
    """
    Processes manifest files belonging to REDIST in ./redistrib_manifests/REDIST, writing the results to
    ./feature_manifests/REDIST.
    """

    # Lazily import so our callback on log_level sets the logging level first.
    from .process_manifests_impl import process_manifests_impl  # noqa: PLC0415

    # Create the version constraint
    version_constraint = VersionConstraint(
        version_min=min_version,
        version_max=max_version,
        version=version,
    )
    process_manifests_impl(
        redist=redist,
        cleanup=cleanup,
        no_parallel=no_parallel,
        version_constraint=version_constraint,
    )


@main.command()
def print_manifest_schema() -> None:
    import json  # noqa: PLC0415

    from cuda_redist_find_features.manifest.nvidia import NvidiaManifestTA  # noqa: PLC0415

    print(json.dumps(NvidiaManifestTA.json_schema(), indent=2))


@main.command()
def print_feature_schema() -> None:
    import json  # noqa: PLC0415

    from cuda_redist_find_features.manifest.feature.manifest import FeatureManifest  # noqa: PLC0415

    print(json.dumps(FeatureManifest.model_json_schema(), indent=2))
