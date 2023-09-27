import logging
from functools import lru_cache
from pathlib import Path


def cache_hit_ratio(hits: int, misses: int, _maxsize: None | int, _currsize: int) -> float:
    calls = hits + misses
    return hits / calls if calls else 0.0


@lru_cache
def _exists(path: Path) -> bool:
    """
    Returns whether the given path exists.
    """
    return path.exists()


@lru_cache
def _is_dir(path: Path) -> bool:
    """
    Returns whether the given path is a directory.
    """
    return path.is_dir()


@lru_cache
def _iterdir(path: Path) -> list[Path]:
    """
    Returns the contents of the given path.
    """
    return list(path.iterdir())


@lru_cache
def _has_contents(path: Path) -> bool:
    """
    Returns whether the given path has contents.
    """
    return any(True for _ in path.iterdir())


@lru_cache
def _rglob(path: Path, pattern: str, files_only: bool = False) -> list[Path]:
    """
    Returns a list of paths matching the given patterns.
    """
    matched = path.rglob(pattern)
    if files_only:
        matched = (path for path in matched if path.is_file())
    return sorted(matched)


def exists(path: Path) -> bool:
    """
    Returns whether the given path exists.
    """
    path_exists = _exists(path)
    logging.debug(f"Path {path} {'exists' if path_exists else 'does not exist'}")
    logging.debug(f"cache info: {_exists.cache_info()}")
    logging.debug(f"cache hit ratio: {cache_hit_ratio(*_exists.cache_info())}")
    return path_exists


def is_dir(path: Path) -> bool:
    """
    Returns whether the given path is a directory.
    """
    path_is_dir = _is_dir(path)
    logging.debug(f"Path {path} {'is' if path_is_dir else 'is not'} a directory")
    logging.debug(f"cache info: {_is_dir.cache_info()}")
    logging.debug(f"cache hit ratio: {cache_hit_ratio(*_exists.cache_info())}")
    return path_is_dir


def iterdir(path: Path) -> list[Path]:
    """
    Returns the contents of the given path.
    """
    path_iterdir = _iterdir(path)
    logging.debug(f"Path {path} has {len(path_iterdir)} contents")
    logging.debug(f"cache info: {_iterdir.cache_info()}")
    logging.debug(f"cache hit ratio: {cache_hit_ratio(*_iterdir.cache_info())}")
    return path_iterdir


def has_contents(path: Path) -> bool:
    """
    Returns whether the given path has contents.
    """
    path_has_contents = _has_contents(path)
    logging.debug(f"Path {path} {'has' if path_has_contents else 'does not have'} contents")
    logging.debug(f"cache info: {_has_contents.cache_info()}")
    logging.debug(f"cache hit ratio: {cache_hit_ratio(*_has_contents.cache_info())}")
    return path_has_contents


def rglob(path: Path, pattern: str, files_only: bool = False) -> list[Path]:
    """
    Returns a list of paths matching the given patterns.
    """
    matched = _rglob(path, pattern, files_only)
    logging.debug(f"Path {path} has {len(matched)} matches for pattern {pattern}")
    logging.debug(f"cache info: {_rglob.cache_info()}")
    logging.debug(f"cache hit ratio: {cache_hit_ratio(*_rglob.cache_info())}")
    return matched
