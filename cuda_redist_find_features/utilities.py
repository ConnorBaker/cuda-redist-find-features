from pathlib import Path
from typing import Any, Iterable, Iterator


def is_nonempty(it: Iterable[Any]) -> bool:
    """
    Returns True if the iterable is nonempty.
    """
    return any(True for _ in it)


def file_paths_matching(path: Path, globs: Iterable[str]) -> Iterator[Path]:
    """
    Returns a list of files matching the given globs in the directory tree of the given path.
    """
    return (entry for glob in globs for entry in path.rglob(glob) if entry.is_file())
