import json
from concurrent.futures import Future, ProcessPoolExecutor
from functools import partial
from pathlib import Path
from typing import Any, Callable

from pydantic import HttpUrl

from .. import features, manifest
from ..manifest import ManifestRef
from ..version import Version
from ..version_constraint import VersionConstraint
from . import arguments, options
from .__main__ import main


def _write_manifest_features(
    path: Path,
    manifest_features: dict[str, dict[str, Any]],
) -> None:
    with path.open("w") as f:
        json.dump(manifest_features, f, indent=2, sort_keys=True)
        f.write("\n")


def _process_manifests_serial(
    manifest_redists: dict[Path, dict[str, manifest.Package]],
    process_package: Callable[[manifest.Package], features.Package],
) -> None:
    for manifest_path, manifest_redist in manifest_redists.items():
        features_path = manifest_path.with_name(manifest_path.name.replace("redistrib", "redistrib_features"))
        manifest_features: dict[str, dict[str, Any]] = {}
        for package_name, package in manifest_redist.items():
            package_features = process_package(package)
            manifest_features[package_name] = package_features.dict(
                by_alias=True,
                exclude_none=True,
                exclude={"name", "version", "license"},
            )

        _write_manifest_features(features_path, manifest_features)

    return


def _process_manifests_parallel(
    manifest_redists: dict[Path, dict[str, manifest.Package]],
    process_package: Callable[[manifest.Package], features.Package],
) -> None:
    with ProcessPoolExecutor() as executor:
        futures: dict[Path, dict[str, Future[features.Package]]] = {}
        for manifest_path, manifest_redist in manifest_redists.items():
            features_path = manifest_path.with_name(manifest_path.name.replace("redistrib", "redistrib_features"))
            manifest_features_futures: dict[str, Future[features.Package]] = {}

            for package_name, package in manifest_redist.items():
                package_features_future = executor.submit(process_package, package)
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

            _write_manifest_features(features_path, manifest_features)

    return


@main.command()
@arguments.url
@arguments.manifest_dir(exists=True, file_okay=False, dir_okay=True, readable=True, writable=True)
@options.cleanup
@options.debug
@options.no_parallel
@options.min_version
@options.max_version
@options.version
def process_manifests(
    url: HttpUrl,
    manifest_dir: Path,
    cleanup: bool,
    debug: bool,
    no_parallel: bool,
    min_version: None | Version,
    max_version: None | Version,
    version: None | Version,
) -> None:
    """
    Retrieves all manifests matching `redistrib_*.json` in MANIFEST_DIR and processes them, using URL as the
    base of for the relative paths in the manifest.

    Downloads all packages in the manifest, checks them to see what features they provide, and writes a new manifest
    with this information to MANIFEST_DIR.

    URL should not include a trailing slash.

    MANIFEST_DIR should be a directory containing JSON manifest(s).
    """
    # Create the version constraint
    version_constraint = VersionConstraint(min_version, max_version, version)
    # Parse and filter
    refs = ManifestRef.from_ref(manifest_dir, version_constraint)
    # Transform into manifests
    manifest_redists: dict[Path, dict[str, manifest.Package]] = {
        manifest_dir / f"redistrib_{ref.version}.json": ref.parse_manifest() for ref in refs
    }
    # Process them
    process_package = partial(features.process_package, url_prefix=url, cleanup=cleanup)
    if no_parallel:
        _process_manifests_serial(manifest_redists, process_package)
    else:
        _process_manifests_parallel(manifest_redists, process_package)

    return
