from pathlib import Path

from pydantic import HttpUrl

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
    version_constraint = VersionConstraint(min_version, max_version, version)
    # Parse and filter
    refs = NvidiaManifestRef.from_ref(manifest_dir, version_constraint)
    # Transform into nvidia manifests
    nvidia_manifests: dict[Path, NvidiaManifest] = {
        manifest_dir / f"redistrib_{ref.version}.json": ref.parse() for ref in refs
    }
    # Transform and write them
    for path, nvidia_manifest in nvidia_manifests.items():
        feature_manifest = FeatureManifest.of(url, nvidia_manifest, cleanup=cleanup, no_parallel=no_parallel)
        feature_manifest.write(path.with_stem(path.stem.replace("redistrib", "feature")))
