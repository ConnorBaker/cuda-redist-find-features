from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path

from pydantic import FilePath, HttpUrl

from cuda_redist_find_features.version_constraint import VersionConstraint

from ..manifest.nvidia import NvidiaManifestRef
from ..version import Version
from .__main__ import main
from .argument import manifest_dir_argument, url_argument
from .option import debug_option, max_version_option, min_version_option, no_parallel_option, version_option


@main.command()
@url_argument
@manifest_dir_argument(file_okay=False, dir_okay=True)
@debug_option
@no_parallel_option
@min_version_option
@max_version_option
@version_option
def download_manifests(
    url: HttpUrl,
    manifest_dir: Path,
    debug: bool,
    no_parallel: bool,
    min_version: None | Version,
    max_version: None | Version,
    version: None | Version,
) -> None:
    """
    Downloads manifest files found at URL to MANIFEST_DIR.

    URL should not include a trailing slash.

    Neither MANIFEST_DIR nor its parent directory need to exist.

    Example:
        download_manifests https://developer.download.nvidia.com/compute/cutensor/redist /tmp/cutensor_manifests
    """
    # Create the version constraint
    version_constraint = VersionConstraint(
        version_min=min_version,
        version_max=max_version,
        version=version,
    )

    # Parse and filter
    refs = NvidiaManifestRef[HttpUrl].from_ref(url, version_constraint)

    # Ensure directory exists
    manifest_dir.mkdir(parents=True, exist_ok=True)

    # Curry
    func: Callable[[NvidiaManifestRef[HttpUrl]], NvidiaManifestRef[FilePath]] = partial(
        NvidiaManifestRef[HttpUrl].download, dir=manifest_dir
    )

    if no_parallel:
        for _ in map(func, refs):
            pass
        return

    with ProcessPoolExecutor() as executor:
        for _ in executor.map(func, refs):
            pass
        return
