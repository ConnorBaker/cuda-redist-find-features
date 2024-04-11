from collections.abc import Callable
from concurrent.futures import Executor, Future
from dataclasses import dataclass
from typing import Generic, Self, TypeVar, final

from ._future_status import FutureStatus

A = TypeVar("A")
B = TypeVar("B")


@final
@dataclass(frozen=True, order=True, slots=True)
class Task(Generic[A, B]):
    initial: A
    status: FutureStatus
    future: Future[B]

    def update_status(self) -> Self:
        return __class__(
            initial=self.initial,
            status=FutureStatus.of(self.future),
            future=self.future,
        )

    def is_complete(self) -> bool:
        return self.status in {FutureStatus.DONE, FutureStatus.CANCELLED}

    def is_waiting(self) -> bool:
        return self.status == FutureStatus.WAITING

    def is_running(self) -> bool:
        return self.status == FutureStatus.RUNNING

    @classmethod
    def submit(cls, executor: Executor, initial: A, fn: Callable[[A], B]) -> "Task[A, B]":
        return cls(
            initial=initial,
            status=FutureStatus.WAITING,
            future=executor.submit(fn, initial),
        )
