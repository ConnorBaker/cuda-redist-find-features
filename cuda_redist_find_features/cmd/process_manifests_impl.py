import logging
import time
from collections.abc import Iterable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

from pydantic import FilePath, HttpUrl
from rich.live import Live
from rich.table import Table

from cuda_redist_find_features import utilities
from cuda_redist_find_features.manifest.feature import (
    FeatureManifest,
    FeaturePackageDepsUnresolved,
    FeatureRelease,
)
from cuda_redist_find_features.manifest.nvidia import NvidiaManifest, NvidiaManifestRef, NvidiaPackage
from cuda_redist_find_features.types import PackageId, Task, Version, VersionConstraint

logger = utilities.get_logger(__name__)

MyTask = Task[NvidiaPackage, FeaturePackageDepsUnresolved]


def make_grid(height: int, tasks: Iterable[tuple[PackageId, MyTask]]) -> Table:
    grid = Table(box=None, pad_edge=False, expand=True, width=80, min_width=80)
    grid.add_column("Progress", width=10, min_width=10, max_width=10)
    grid.add_column("Name", width=70, min_width=70, max_width=70)

    # Print tasks which are in progress before those that are waiting.
    # Group the tasks by status
    incomplete_tasks: Iterable[tuple[PackageId, MyTask]] = [
        (key, task) for key, task in tasks if MyTask.is_running(task)
    ] + [(key, task) for key, task in tasks if MyTask.is_waiting(task)]

    # Priorities: running > waiting > completed
    # Print tasks which are in progress before those that are waiting.
    for key, task in incomplete_tasks[:height]:
        name = " ".join((key.package_name, key.platform, str(key.version)))
        grid.add_row(task.status.value, name)

    return grid


def process_manifests_impl(
    url: HttpUrl,
    manifest_dir: Path,
    # overrides_json: Path,
    cleanup: bool,
    no_parallel: bool,
    version_constraint: VersionConstraint,
) -> None:
    """
    Retrieves all manifests matching `redistrib_*.json` in MANIFEST_DIR and processes them, using URL as the
    base of for the relative paths in the manifest.

    Downloads all packages in the manifest, checks them to see what features they provide, and writes a new manifest
    with this information to MANIFEST_DIR.

    URL should not include a trailing slash.

    MANIFEST_DIR should be a directory containing JSON manifest(s).
    """
    # Parse and filter
    refs: Sequence[NvidiaManifestRef[FilePath]] = NvidiaManifestRef.from_ref(manifest_dir, version_constraint)

    # Parse references into manifests
    nvidia_manifests: Mapping[FilePath, tuple[Version, NvidiaManifest]] = {
        ref.ref: (ref.version, ref.parse()) for ref in refs
    }

    # TODO(@connorbaker): Dependency resolution is excluded for now because it is not used downstream.
    # No need to bloat the feature manifests.

    # Load dependencies resolver
    # if overrides_json.exists():
    #     dep_resolver = FeaturePackageDepsResolver.model_validate_json(overrides_json.read_bytes())
    # else:
    #     dep_resolver = FeaturePackageDepsResolver.model_validate({})

    # Curry
    fn = partial(FeaturePackageDepsUnresolved.of, url, cleanup=cleanup)

    # If logging level is less than or equal to warning severity, display the table.
    display_table = utilities.LOGGING_LEVEL >= logging.WARNING

    with (
        Live(auto_refresh=False) as live,
        ThreadPoolExecutor(max_workers=1 if no_parallel else None) as executor,
    ):
        # Initial tasks
        tasks: Mapping[PackageId, MyTask] = {
            PackageId(platform, package_name, version): Task.submit(
                executor,
                package,
                fn,
            )
            for _, (version, manifest) in nvidia_manifests.items()
            for package_name, release in manifest.releases.items()
            for platform, package in release.packages.items()
        }

        # Update the table
        if display_table:
            live.update(make_grid(live.console.height, tasks.items()), refresh=True)

        # Wait for all of the downloads to complete
        while not all(map(MyTask.is_complete, tasks.values())):
            # Update the table
            tasks = {url: task.update_status() for url, task in tasks.items()}
            if display_table:
                live.update(make_grid(live.console.height, tasks.items()), refresh=True)

            # Wait a bit
            time.sleep(0.1)

    flattened_unresolved_tree: Mapping[PackageId, FeaturePackageDepsUnresolved] = {
        package_id: task.future.result() for package_id, task in tasks.items()
    }

    # Update DependenciesResolver with the content of dependencies (that is, the new feature manifest we are in
    # the process of constructing)
    # dep_resolver = dep_resolver.bulk_add_lib_provider(flattened_unresolved_tree)

    # Dump DependenciesResolver to overrides_json
    # dep_resolver.write(overrides_json)

    # Resolve dependencies
    # flattened_resolved_tree: Mapping[PackageId, FeaturePackageDepsResolved] = {
    #     package_id: FeaturePackageDepsResolved.of(package_id, feature_package, dep_resolver)
    #     for package_id, feature_package in flattened_unresolved_tree.items()
    # }

    # Organize the results
    feature_manifests: Mapping[FilePath, FeatureManifest[FeaturePackageDepsUnresolved]] = {
        file_path: FeatureManifest[FeaturePackageDepsUnresolved].model_validate({
            package_name: FeatureRelease[FeaturePackageDepsUnresolved].model_validate({
                platform: flattened_unresolved_tree[PackageId(platform, package_name, version)]
                for platform in release.packages.keys()
            })
            for package_name, release in manifest.releases.items()
        })
        for file_path, (version, manifest) in nvidia_manifests.items()
    }

    # Write the results
    for file_path, feature_manifest in feature_manifests.items():
        feature_manifest_path = file_path.with_stem(file_path.stem.replace("redistrib", "feature"))
        feature_manifest.write(feature_manifest_path)
