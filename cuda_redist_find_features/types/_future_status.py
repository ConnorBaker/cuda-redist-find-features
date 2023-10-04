from concurrent.futures import Future
from enum import Enum
from typing import Any, Self, final


@final
class FutureStatus(Enum):
    WAITING = ":zzz:"
    RUNNING = ":clock5:"
    DONE = ":white_check_mark:"
    CANCELLED = ":x:"

    @classmethod
    def of(cls, future: Future[Any]) -> Self:
        if future.cancelled():
            return cls.CANCELLED
        elif future.done():
            return cls.DONE
        elif future.running():
            return cls.RUNNING
        else:
            return cls.WAITING
