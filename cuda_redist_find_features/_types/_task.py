from collections.abc import Callable
from concurrent.futures import Executor, Future
from dataclasses import dataclass
from typing import Self, final

from ._future_status import FutureStatus


@final
@dataclass(frozen=True, order=True, slots=True)
class Task[T]:
    status: FutureStatus
    future: Future[T]

    def update_status(self) -> Self:
        return self.__class__(
            status=FutureStatus.of(self.future),
            future=self.future,
        )

    def is_complete(self) -> bool:
        return self.status in {FutureStatus.DONE, FutureStatus.CANCELLED}

    def is_incomplete(self) -> bool:
        return not self.is_complete()

    def is_waiting(self) -> bool:
        return self.status == FutureStatus.WAITING

    def is_running(self) -> bool:
        return self.status == FutureStatus.RUNNING

    @classmethod
    def submit[**As](cls, executor: Executor, fn: Callable[As, T], /, *args: As.args, **kwargs: As.kwargs) -> "Task[T]":
        return cls(
            status=FutureStatus.WAITING,
            future=executor.submit(fn, *args, **kwargs),
        )
