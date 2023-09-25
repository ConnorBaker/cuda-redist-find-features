import logging
from dataclasses import dataclass
from pathlib import Path

from .types import FeatureDetector


@dataclass
class DirDetector(FeatureDetector):
    """
    Detects the presence of non-empty directory.
    """

    dir: Path

    def detect(self, tree: Path) -> bool:
        path = tree / self.dir
        if not path.exists():
            logging.debug(f"Did not find directory: {path}")
            return False
        if not path.is_dir():
            logging.debug(f"Found file instead of directory: {path}")
            return False
        if not any(path.rglob("*")):
            logging.debug(f"Found empty directory: {path}")
            return False

        logging.debug(f"Found non-empty directory: {path}")
        return True
