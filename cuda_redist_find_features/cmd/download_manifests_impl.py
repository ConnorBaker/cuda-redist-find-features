import logging
import time
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import FilePath, HttpUrl
from rich.live import Live
from rich.table import Table

from cuda_redist_find_features import utilities
from cuda_redist_find_features._types import RedistName, Task, Version, VersionConstraint, get_redist_url_prefix
from cuda_redist_find_features.manifest.nvidia import NvidiaManifestRef

MyTask = Task[NvidiaManifestRef[FilePath]]


def make_grid(height: int, tasks: Iterable[tuple[Version, MyTask]]) -> Table:
    grid = Table(box=None, pad_edge=False, expand=True, width=80, min_width=80)
    grid.add_column("Progress", width=10, min_width=10, max_width=10)
    grid.add_column("Version", width=70, min_width=70, max_width=70)

    # Print tasks which are in progress before those that are waiting.
    # Group the tasks by status
    incomplete_tasks: Iterable[tuple[Version, MyTask]] = [
        (key, task) for key, task in tasks if MyTask.is_running(task)
    ] + [(key, task) for key, task in tasks if MyTask.is_waiting(task)]

    # Priorities: running > waiting > completed
    # Print tasks which are in progress before those that are waiting.
    for key, task in incomplete_tasks[:height]:
        name = str(key)
        grid.add_row(task.status.value, name)

    return grid


def download_manifests_impl(
    redist: RedistName,
    no_parallel: bool,
    version_constraint: VersionConstraint,
) -> None:
    redistrib_manifests_dir = Path("redistrib_manifests") / redist

    url_prefix = get_redist_url_prefix(redist)

    # Parse and filter
    manifest_refs = NvidiaManifestRef[HttpUrl].from_ref(url_prefix, version_constraint)

    # Ensure directory exists
    redistrib_manifests_dir.mkdir(parents=True, exist_ok=True)

    # If logging level is less than or equal to warning severity, display the table.
    display_table = utilities.LOGGING_LEVEL >= logging.WARNING

    with (
        Live(auto_refresh=False) as live,
        ThreadPoolExecutor(max_workers=1 if no_parallel else None) as executor,
    ):
        # Initial tasks
        tasks: dict[Version, MyTask] = {
            manifest_ref.version: Task[NvidiaManifestRef[FilePath]].submit(
                executor,
                NvidiaManifestRef[HttpUrl].download,
                manifest_ref,
                redistrib_manifests_dir,
            )
            for manifest_ref in manifest_refs
        }

        if display_table:
            live.update(make_grid(live.console.height, tasks.items()), refresh=True)

        # Wait for all of the downloads to complete
        while any(map(MyTask.is_incomplete, tasks.values())):
            # Update the table
            for version in tasks:
                tasks[version] = tasks[version].update_status()

            if display_table:
                live.update(make_grid(live.console.height, tasks.items()), refresh=True)

            # Wait a bit
            time.sleep(0.1)
