from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from typing_extensions import override

from cuda_redist_find_features.utilities import get_logger

from .dir import DirDetector
from .types import FeatureDetector
from .utilities import cached_path_rglob

logger = get_logger(__name__)


@dataclass
class DynamicLibraryDetector(FeatureDetector[Sequence[Path]]):
    """
    Detects the presence of a dynamic library in the `lib` directory.
    """

    @override
    def find(self, store_path: Path) -> None | Sequence[Path]:
        """
        Finds paths of dynamic libraries under `lib` within the given Nix store path.
        """
        lib_dir = DirDetector(Path("lib")).find(store_path)
        if lib_dir is None:
            return None

        dynamic_libraries = cached_path_rglob(lib_dir, "*.so", files_only=True)
        if [] != dynamic_libraries:
            logger.debug("Found dynamic libraries: %s.", dynamic_libraries)
            return dynamic_libraries

        return None
