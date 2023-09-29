from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path

from pydantic import FilePath, HttpUrl

from ..manifest.feature import FeatureManifest
from ..manifest.nvidia import NvidiaManifest, NvidiaManifestRef
from ..version import Version
from ..version_constraint import VersionConstraint
from .__main__ import main
from .argument import manifest_dir_argument, url_argument
from .option import (
    cleanup_option,
    debug_option,
    max_version_option,
    min_version_option,
    no_parallel_option,
    version_option,
)


# Undecorate the NvidiaManifestRef download method so it can be pickled.
def _handler(url: HttpUrl, cleanup: bool, nvidia_manifest_path: FilePath, nvidia_manifest: NvidiaManifest) -> FilePath:
    """ """
    feature_manifest_path = nvidia_manifest_path.with_stem(nvidia_manifest_path.stem.replace("redistrib", "feature"))
    feature_manifest = FeatureManifest.of(url, nvidia_manifest, cleanup)
    feature_manifest.write(feature_manifest_path)
    return feature_manifest_path


@main.command()
@url_argument
@manifest_dir_argument(exists=True, file_okay=False, dir_okay=True, readable=True, writable=True)
@cleanup_option
@debug_option
@no_parallel_option
@min_version_option
@max_version_option
@version_option
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
    version_constraint = VersionConstraint(
        version_min=min_version,
        version_max=max_version,
        version=version,
    )

    # Parse and filter
    refs: Sequence[NvidiaManifestRef[FilePath]] = NvidiaManifestRef.from_ref(manifest_dir, version_constraint)

    # Parse references into manifests
    nvidia_manifests: Mapping[FilePath, NvidiaManifest] = {ref.ref: ref.parse() for ref in refs}

    # Curry
    func: Callable[[FilePath, NvidiaManifest], FilePath] = partial(_handler, url, cleanup)

    if no_parallel:
        for _ in map(func, *zip(*nvidia_manifests.items())):
            pass
        return

    with ProcessPoolExecutor() as executor:
        for _ in executor.map(func, *zip(*nvidia_manifests.items())):
            pass
        return
