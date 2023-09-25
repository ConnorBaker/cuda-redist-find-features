import logging
from dataclasses import dataclass
from pathlib import Path

from .dir import DirDetector


def file_is_unix_executable(file: Path) -> bool:
    return bool(file.stat().st_mode & 0o111)


def file_is_windows_executable(file: Path) -> bool:
    # Yes, I know DLLs are not executables, but they are okay to exist in the bin directory.
    return file.suffix in {".bat", ".dll", ".exe"}


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
            executable
            for executable in path.rglob("*")
            if executable.is_file() and (file_is_unix_executable(executable) or file_is_windows_executable(executable))
        ]
        logging.debug(f"Found executables: {executables}")
        has_executables = [] != executables
        if not has_executables:
            # Binary directory which is non-empty but does not contain any executables
            logging.warning(f"Found bin directory without executable files: {path}")
        return has_executables
