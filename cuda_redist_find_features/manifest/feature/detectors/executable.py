import logging
from dataclasses import dataclass
from pathlib import Path

from .dir import DirDetector


@dataclass
class ExecutableDetector(DirDetector):
    """
    Detects the presence of an executable in the bin directory.
    """

    dir: Path = Path("bin")

    def detect(self, tree: Path) -> bool:
        if not super().detect(tree):
            return False

        path = tree / self.dir
        executables = [
            executable for executable in path.rglob("*") if executable.is_file() and executable.stat().st_mode & 0o111
        ]
        has_executables = [] != executables
        if not has_executables:
            logging.info(f"Found bin directory without executable files: {path}")
            return False
        logging.debug(f"Found executables: {executables}")
        logging.info(f"Found executables: {has_executables}")
        return has_executables
