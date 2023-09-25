import logging
from dataclasses import dataclass
from pathlib import Path

from .dir import DirDetector


@dataclass
class StaticLibraryDetector(DirDetector):
    """
    Detects the presence of a static library in the lib directory.
    """

    dir: Path = Path("lib")

    def detect(self, tree: Path) -> bool:
        if not super().detect(tree):
            return False

        path = tree / self.dir

        static_libraries = [library for library in path.rglob("*.a") if library.is_file()]
        logging.debug(f"Found static libraries: {static_libraries}")
        has_static_libraries = [] != static_libraries
        return has_static_libraries
