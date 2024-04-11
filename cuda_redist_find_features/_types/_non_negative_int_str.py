from typing import Annotated

from pydantic import TypeAdapter

from ._pydantic import PydanticFrozenField, PydanticTypeAdapter

type NonNegativeIntStr = Annotated[
    str,
    PydanticFrozenField(
        description="An MD5 hash.",
        examples=["512", "024", "0"],
        pattern=r"[0-9]+",
    ),
]

NonNegativeIntStrTA: TypeAdapter[NonNegativeIntStr] = PydanticTypeAdapter(NonNegativeIntStr)
