from concurrent.futures import Future, ProcessPoolExecutor
from pathlib import Path

from pydantic import HttpUrl

from ..manifest import ManifestRef
from ..version import Version
from ..version_constraint import VersionConstraint
from . import arguments, options
from .__main__ import main


@main.command()
@arguments.url
@arguments.manifest_dir(file_okay=False, dir_okay=True)
@options.debug
@options.no_parallel
@options.min_version
@options.max_version
@options.version
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
    version_constraint = VersionConstraint(min_version, max_version, version)
    # Parse and filter
    refs = ManifestRef.from_ref(url, version_constraint)
    # Download them
    if no_parallel:
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
