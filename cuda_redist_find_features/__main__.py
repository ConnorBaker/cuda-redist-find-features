import json
import logging
from concurrent.futures import Future, ProcessPoolExecutor
from pathlib import Path
from typing import Any

import click
import pydantic
from pydantic import HttpUrl

from cuda_redist_find_features import features, manifest
from cuda_redist_find_features.manifest import ManifestRef
from cuda_redist_find_features.version import Version
from cuda_redist_find_features.version_constraint import VersionConstraint


class HttpUrlOption(click.ParamType):
    name: str = "url"

    def convert(self, value: str, param: None | click.Parameter, ctx: None | click.Context) -> HttpUrl:
        try:
            return pydantic.parse_obj_as(HttpUrl, value)
        except ValueError as err:
            self.fail(f"{value} is not a valid URL: {err}", param, ctx)


HTTP_URL_OPTION = HttpUrlOption()


class VersionOption(click.ParamType):
    name: str = "version"

    def convert(self, value: str, param: None | click.Parameter, ctx: None | click.Context) -> Version:
        try:
            return Version.parse(value)
        except ValueError:
            self.fail(f"{value} is not a valid version string", param, ctx)


VERSION_OPTION = VersionOption()


@click.group()
@click.option("--debug/--no-debug", type=bool, default=False)
@click.option("--no-parallel/--parallel", type=bool, default=False, help="Disable parallel processing.")
@click.option(
    "--min-version", type=VERSION_OPTION, default=None, help="Minimum version to accept. Exclusive with --version."
)
@click.option(
    "--max-version", type=VERSION_OPTION, default=None, help="Maximum version to accept. Exclusive with --version."
)
@click.option(
    "--version",
    type=VERSION_OPTION,
    default=None,
    help=" ".join(
        [
            "Version to accept.",
            "If not specified, operates on all versions.",
            "Exclusive with --min-version and --max-version.",
        ]
    ),
)
@click.pass_context
def main(
    ctx: click.Context,
    debug: bool,
    no_parallel: bool,
    min_version: None | Version,
    max_version: None | Version,
    version: None | Version,
) -> None:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="[%(asctime)s][PID%(process)s][%(funcName)s][%(levelname)s] %(message)s",
        # Use ISO8601 format for the timestamp
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    ctx.ensure_object(dict)

    if no_parallel:
        logging.info("Parallel processing disabled.")

    ctx.obj["no_parallel"] = no_parallel
    ctx.obj["version_constraint"] = VersionConstraint(min_version, max_version, version)
    return


@main.command()
@click.argument("url", type=HTTP_URL_OPTION)
@click.argument("manifest_dir", type=click.Path(file_okay=False, dir_okay=True, path_type=Path))
@click.pass_context
def download_manifests(
    ctx: click.Context,
    url: HttpUrl,
    manifest_dir: Path,
) -> None:
    """
    Downloads manifest files found at URL to MANIFEST_DIR.

    URL should not include a trailing slash.

    Neither MANIFEST_DIR nor its parent directory need to exist.

    Example:
        download_manifests https://developer.download.nvidia.com/compute/cutensor/redist /tmp/cutensor_manifests
    """
    # Parse and filter
    refs = ManifestRef.from_ref(url, ctx.obj["version_constraint"])
    # Download them
    if ctx.obj["no_parallel"]:
        for ref in refs:
            ref.download(manifest_dir)
        return

    with ProcessPoolExecutor() as executor:
        futures: list[Future[Path]] = [executor.submit(ref.download, manifest_dir) for ref in refs]

        # Wait for all futures to complete.
        executor.shutdown(wait=True)

        # Check for exceptions
        for future in futures:
            future.result()

    # Done
    return


@main.command()
@click.argument("url_prefix", type=HTTP_URL_OPTION)
@click.argument(
    "manifest_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, writable=True, path_type=Path),
)
@click.option("--cleanup/--no-cleanup", type=bool, default=False, help="Delete downloaded files after processing.")
@click.pass_context
def process_manifests(
    ctx: click.Context,
    url_prefix: HttpUrl,
    manifest_dir: Path,
    cleanup: bool,
) -> None:
    """
    Retrieves all manifests matching `redistrib_*.json` in MANIFEST_DIR and processes them, using URL_PREFIX as the
    base URL.

    Downloads all packages in the manifest, checks them to see what features they provide, and writes a new manifest
    with this information to MANIFEST_DIR.

    URL_PREFIX should not include a trailing slash.

    MANIFEST_DIR should be a directory containing JSON manifest(s).
    """
    # Parse and filter
    refs = ManifestRef.from_ref(manifest_dir, ctx.obj["version_constraint"])
    # Transform into manifests
    manifest_redists: dict[Path, dict[str, manifest.Package]] = {
        manifest_dir / f"redistrib_{ref.version}.json": ref.parse_manifest() for ref in refs
    }
    # Process them
    if ctx.obj["no_parallel"]:
        for manifest_path, manifest_redist in manifest_redists.items():
            features_path = manifest_path.with_name(manifest_path.name.replace("redistrib", "redistrib_features"))
            manifest_features: dict[str, Any] = {}
            for package_name, package in manifest_redist.items():
                package_features = features.process_package(package, url_prefix, cleanup)
                dict_str = package_features.dict(
                    by_alias=True,
                    exclude_none=True,
                    exclude={"name", "version", "license"},
                )
                manifest_features[package_name] = dict_str

            with features_path.open("w") as f:
                json.dump(manifest_features, f, indent=2, sort_keys=True)
                f.write("\n")

    with ProcessPoolExecutor() as executor:
        futures: dict[Path, dict[str, Future[features.Package]]] = {}
        for manifest_path, manifest_redist in manifest_redists.items():
            features_path = manifest_path.with_name(manifest_path.name.replace("redistrib", "redistrib_features"))
            manifest_features_futures: dict[str, Future[features.Package]] = {}

            for package_name, package in manifest_redist.items():
                package_features_future = executor.submit(features.process_package, package, url_prefix, cleanup)
                manifest_features_futures[package_name] = package_features_future

            futures[features_path] = manifest_features_futures

        # Wait for all futures to complete.
        executor.shutdown(wait=True)

        # Check for exceptions
        for features_path, manifest_features_futures in futures.items():
            manifest_features = {}

            for package_name, package_features_future in manifest_features_futures.items():
                package_features = package_features_future.result()
                dict_str = package_features.dict(
                    by_alias=True,
                    exclude_none=True,
                    exclude={"name", "version", "license"},
                )
                manifest_features[package_name] = dict_str

            with features_path.open("w") as f:
                json.dump(manifest_features, f, indent=2, sort_keys=True)
                f.write("\n")
