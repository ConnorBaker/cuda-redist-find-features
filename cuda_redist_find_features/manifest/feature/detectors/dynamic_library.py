import logging
from dataclasses import dataclass
from pathlib import Path

from .dir import DirDetector


@dataclass
class DynamicLibraryDetector(DirDetector):
    """
    Detects the presence of a dynamic library in the lib directory.
    """

    dir: Path = Path("lib")

    def detect(self, tree: Path) -> bool:
        if not super().detect(tree):
            return False

        path = tree / self.dir
        dynamic_libraries = [library for library in path.rglob("*.so") if library.is_file()]
        logging.debug(f"Found dynamic libraries: {dynamic_libraries}")
        has_dynamic_libraries = [] != dynamic_libraries
        return has_dynamic_libraries
