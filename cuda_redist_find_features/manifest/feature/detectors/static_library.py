import logging
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from typing_extensions import override

from .dir import DirDetector
from .types import FeatureDetector
from .utilities import cached_path_rglob


@dataclass
class StaticLibraryDetector(FeatureDetector[Sequence[Path]]):
    """
    Detects the presence of a static library in the `lib` directory.
    """

    @override
    def find(self, store_path: Path) -> None | Sequence[Path]:
        """
        Finds paths of static libraries under `lib` within the given Nix store path.
        """
        lib_dir = DirDetector(Path("lib")).find(store_path)
        if lib_dir is None:
            return None

        static_libraries = cached_path_rglob(lib_dir, "*.a", files_only=True)
        if [] != static_libraries:
            logging.debug(f"Found static libraries: {static_libraries}")
            return static_libraries

        return None
