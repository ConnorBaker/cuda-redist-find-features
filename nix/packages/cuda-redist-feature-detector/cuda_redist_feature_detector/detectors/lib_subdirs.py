from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import override

from cuda_redist_lib.logger import get_logger

from .dir import DirDetector
from .types import FeatureDetector

logger = get_logger(__name__)


@dataclass
class LibSubdirsDetector(FeatureDetector[Sequence[Path]]):
    """
    Detects the presence of non-empty subdirectories under `lib`.
    """

    @override
    def find(self, store_path: Path) -> None | Sequence[Path]:
        """
        Finds paths of non-empty subdirectories under `lib` within the given Nix store path.
        """
        lib_dir = DirDetector(Path("lib")).find(store_path)
        if lib_dir is None:
            return None

        lib_subdirs = sorted(
            subdir.relative_to(lib_dir)
            for path in lib_dir.iterdir()
            if path.is_dir() and (subdir := DirDetector(path).find(lib_dir)) is not None
        )

        if [] != lib_subdirs:
            logger.debug("Found non-empty subdirectories under `lib`: %s.", lib_subdirs)
            return lib_subdirs

        return None
