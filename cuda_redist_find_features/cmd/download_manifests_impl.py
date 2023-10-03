from __future__ import annotations

import logging
import time
from collections.abc import Iterable, Mapping
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

from pydantic import FilePath, HttpUrl
from rich.live import Live
from rich.table import Table

from cuda_redist_find_features import utilities
from cuda_redist_find_features.manifest.nvidia import NvidiaManifestRef
from cuda_redist_find_features.types import Task
from cuda_redist_find_features.version_constraint import VersionConstraint

MyTask = Task[NvidiaManifestRef[HttpUrl], NvidiaManifestRef[FilePath]]


def make_grid(height: int, tasks: Iterable[MyTask]) -> Table:
    grid = Table(box=None, pad_edge=False, expand=True, width=80, min_width=80)
    grid.add_column("Progress", width=10, min_width=10, max_width=10)
    grid.add_column("Version", width=70, min_width=70, max_width=70)

    # Group the tasks by status
    incomplete_tasks: Iterable[MyTask] = [task for task in tasks if MyTask.is_running(task)] + [
        task for task in tasks if MyTask.is_waiting(task)
    ]

    # Priorities: running > waiting > completed
    # Print tasks which are in progress before those that are waiting.
    for task in incomplete_tasks[:height]:
        grid.add_row(task.status.value, str(task.initial.version))

    return grid


def download_manifests_impl(
    url: HttpUrl,
    manifest_dir: Path,
    no_parallel: bool,
    version_constraint: VersionConstraint,
) -> None:
    """
    Downloads manifest files found at URL to MANIFEST_DIR.

    URL should not include a trailing slash.

    Neither MANIFEST_DIR nor its parent directory need to exist.

    Example:
        download_manifests https://developer.download.nvidia.com/compute/cutensor/redist /tmp/cutensor_manifests
    """
    # Parse and filter
    manifest_refs = NvidiaManifestRef[HttpUrl].from_ref(url, version_constraint)

    # Ensure directory exists
    manifest_dir.mkdir(parents=True, exist_ok=True)

    # Curry
    fn = partial(NvidiaManifestRef[HttpUrl].download, dir=manifest_dir)

    # If logging level is less than or equal to warning severity, display the table.
    display_table = utilities.LOGGING_LEVEL >= logging.WARNING

    with (
        Live(auto_refresh=False) as live,
        ThreadPoolExecutor(max_workers=1 if no_parallel else None) as executor,
    ):
        # Initial tasks
        tasks: Mapping[HttpUrl, MyTask] = {
            manifest_ref.ref: Task.submit(
                executor,
                manifest_ref,
                fn,
            )
            for manifest_ref in manifest_refs
        }

        if display_table:
            live.update(make_grid(live.console.height, tasks.values()), refresh=True)

        # Wait for all of the downloads to complete
        while not all(map(MyTask.is_complete, tasks.values())):
            # Update the table
            tasks = {url: task.update_status() for url, task in tasks.items()}
            if display_table:
                live.update(make_grid(live.console.height, tasks.values()), refresh=True)

            # Wait a bit
            time.sleep(0.1)
