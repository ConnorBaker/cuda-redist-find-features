from collections.abc import Sequence
from typing import Literal, cast, get_args

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LogLevels = cast(Sequence[LogLevel], get_args(LogLevel))
