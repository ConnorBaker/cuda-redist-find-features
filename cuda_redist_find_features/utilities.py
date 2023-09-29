from __future__ import annotations

from builtins import map as _map
from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import ProcessPoolExecutor
from typing import Any, TypeVar

# Helper for parallel execution
T = TypeVar("T")


def map(fn: Callable[..., T], *iterables: Iterable[Any], no_parallel: bool = False) -> Iterator[T]:
    if no_parallel:
        return _map(fn, *iterables)
    else:
        import pickle

        pickle.DEFAULT_PROTOCOL = pickle.HIGHEST_PROTOCOL

        with ProcessPoolExecutor() as executor:
            return executor.map(fn, *iterables)
