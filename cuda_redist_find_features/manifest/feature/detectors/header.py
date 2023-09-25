import logging
from dataclasses import dataclass
from pathlib import Path

from .dir import DirDetector


@dataclass
class HeaderDetector(DirDetector):
    """
    Detects the presence of headers in the include directory.
    """

    dir: Path = Path("include")

    def detect(self, tree: Path) -> bool:
        if not super().detect(tree):
            return False

        path = tree / self.dir
        headers = [
            header for header in path.rglob("*") if header.is_file() and header.suffix in {".h", ".hh", ".hpp", ".hxx"}
        ]
        logging.debug(f"Found headers: {headers}")
        has_headers = [] != headers
        return has_headers
