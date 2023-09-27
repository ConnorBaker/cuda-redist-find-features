from abc import abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

from .dir import DirDetector
from .types import FeatureDetector
from .utilities import cached_path_iterdir

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

    RichlyComparable = TypeVar("RichlyComparable", bound=SupportsRichComparison)
else:
    RichlyComparable = TypeVar("RichlyComparable")


@dataclass
class GroupableFeatureDetector(FeatureDetector[list[RichlyComparable] | dict[Path, list[RichlyComparable]]]):
    """
    A detector that detects a feature or a group of features. Given a directory, ensures that there are subdirectories
    if and only if there are no files directly under the directory. In the case there are no subdirectories, the
    detector will return a list of features. In the case there are subdirectories, the detector will return a
    dictionary mapping each subdirectory to a list of features.
    """

    dir: Path
    ignored_dirs: set[Path]

    @staticmethod
    @abstractmethod
    def path_feature_detector(path: Path) -> set[RichlyComparable]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def path_filter(path: Path) -> bool:
        raise NotImplementedError

    def paths_func(self, paths: Iterable[Path]) -> list[RichlyComparable]:
        """
        Operates on a list of paths and accumulates the results of `self.path_feature_detector` on each path.

        Applies `self.path_filter` to each path before passing it to `self.path_feature_detector`.

        Returns a sorted, deduplicated list of features.
        """
        return sorted(
            reduce(
                set.union,  # type: ignore[arg-type]
                map(self.path_feature_detector, filter(self.path_filter, paths)),
                set(),
            )
        )

    def find(self, store_path: Path) -> None | list[RichlyComparable] | dict[Path, list[RichlyComparable]]:
        # Ensure that store_path is a directory which exists and is non-empty.
        absolute_dir: None | Path = DirDetector(self.dir).find(store_path)
        if absolute_dir is None:
            return None

        items = cached_path_iterdir(absolute_dir)

        # Get rid of the ignored directories.
        absolute_ignored_dirs = {absolute_dir / ignored_dir for ignored_dir in self.ignored_dirs}
        items = [item for item in items if item not in absolute_ignored_dirs and self.path_filter(item)]

        # If there are no items, return None.
        if [] == items:
            return None

        # Make sure that if there are subdirectories, there are no items directly under the directory, and vice versa.
        all_items_are_dirs = all(item.is_dir() for item in items)
        all_items_are_files = all(item.is_file() for item in items)
        if not (all_items_are_dirs ^ all_items_are_files):
            raise RuntimeError(f"Found both subdirectories and items directly under {absolute_dir}: {items}.")

        if all_items_are_files:
            return self.paths_func(items)
        else:
            return {subdir.relative_to(absolute_dir): self.paths_func(cached_path_iterdir(subdir)) for subdir in items}
