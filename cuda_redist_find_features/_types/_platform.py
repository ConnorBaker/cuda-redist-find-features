from collections.abc import Iterable
from typing import Annotated, Literal, cast, get_args

from pydantic import TypeAdapter

from ._pydantic import PydanticFrozenField, PydanticTypeAdapter

_Platform = Literal[
    "linux-aarch64",
    "linux-ppc64le",
    "linux-sbsa",
    "linux-x86_64",
    "windows-x86_64",
]
type Platform = Annotated[
    _Platform,
    # NOTE: Cannot use strict with literals/unions.
    PydanticFrozenField(description="A platform name."),
]
Platforms = cast(Iterable[Platform], get_args(_Platform))
PlatformTA: TypeAdapter[Platform] = PydanticTypeAdapter(Platform)
