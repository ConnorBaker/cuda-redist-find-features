import logging
import time
from collections.abc import Iterable, Mapping
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import FilePath
from rich.live import Live
from rich.table import Table

from cuda_redist_find_features import utilities
from cuda_redist_find_features._types import RedistName, Task, Version, VersionConstraint, get_redist_url_prefix
from cuda_redist_find_features.manifest.feature.manifest import FeatureManifest
from cuda_redist_find_features.manifest.nvidia import NvidiaManifest, NvidiaManifestRef

logger = utilities.get_logger(__name__)

MyTask = Task[FeatureManifest]


def make_grid(height: int, tasks: Iterable[tuple[FilePath, MyTask]]) -> Table:
    grid = Table(box=None, pad_edge=False, expand=True, width=80, min_width=80)
    grid.add_column("Progress", width=10, min_width=10, max_width=10)
    grid.add_column("Name", width=70, min_width=70, max_width=70)

    # Print tasks which are in progress before those that are waiting.
    # Group the tasks by status
    incomplete_tasks: Iterable[tuple[FilePath, MyTask]] = [
        (key, task) for key, task in tasks if MyTask.is_running(task)
    ] + [(key, task) for key, task in tasks if MyTask.is_waiting(task)]

    # Priorities: running > waiting > completed
    # Print tasks which are in progress before those that are waiting.
    for key, task in incomplete_tasks[:height]:
        name = key.as_posix()
        grid.add_row(task.status.value, name)

    return grid


def process_manifests_impl(
    redist: RedistName,
    cleanup: bool,
    no_parallel: bool,
    version_constraint: VersionConstraint,
) -> None:
    """
    Retrieves all manifests matching `redistrib_*.json` in ./redistrib_manifests and processes them, using URL as the
    base of for the relative paths in the manifest.

    Downloads all packages in the manifest, checks them to see what features they provide, and writes a new manifest
    with this information to ./feature_manifests.

    URL should not include a trailing slash.
    """
    redistrib_manifests_dir = Path("redistrib_manifests") / redist
    feature_manifests_dir = Path("feature_manifests") / redist

    url_prefix = get_redist_url_prefix(redist)

    # Ensure directory exists
    feature_manifests_dir.mkdir(parents=True, exist_ok=True)

    # Parse references into manifests
    nvidia_manifests: Mapping[tuple[FilePath, Version], NvidiaManifest] = {
        (ref.ref, ref.version): ref.parse()
        for ref in NvidiaManifestRef[FilePath].from_ref(redistrib_manifests_dir, version_constraint)
    }

    # If logging level is less than or equal to warning severity, display the table.
    display_table = utilities.LOGGING_LEVEL >= logging.WARNING

    with (
        Live(auto_refresh=False) as live,
        ThreadPoolExecutor(max_workers=1 if no_parallel else None) as executor,
    ):
        # TODO: Structuring parallelism in this way ensures that only one manifest is processed at a time --
        # we really want to process multiple packages in parallel!
        # Initial tasks
        tasks: dict[FilePath, MyTask] = {
            path: Task.submit(
                executor,
                FeatureManifest.of,
                name=path.stem,
                version=version,
                url_prefix=url_prefix,
                manifest=manifest,
                cleanup=cleanup,
            )
            for (path, version), manifest in nvidia_manifests.items()
        }

        # Update the table
        if display_table:
            live.update(make_grid(live.console.height, tasks.items()), refresh=True)

        # Wait for all of the downloads to complete
        while any(map(MyTask.is_incomplete, tasks.values())):
            # Update the table
            for path in tasks:
                tasks[path] = tasks[path].update_status()

            if display_table:
                live.update(make_grid(live.console.height, tasks.items()), refresh=True)

            # Wait a bit
            time.sleep(0.1)

    # Write the results
    # NOTE: We avoid using a callback because things are more complicated than just writing the results.
    for path, flattened_manifest in tasks.items():
        flattened_manifest.future.result().write(feature_manifests_dir / path.name.replace("redistrib", "feature"))
