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
            logging.info(f"Did not find directory: {path}")
            return False
        if not path.is_dir():
            logging.info(f"Found file instead of directory: {path}")
            return False
        if not any(path.rglob("*")):
            logging.info(f"Found empty directory: {path}")
            return False

        logging.info(f"Found non-empty directory: {path}")
        return True
