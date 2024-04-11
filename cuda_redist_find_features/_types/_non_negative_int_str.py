from typing import Annotated

from pydantic import Field, TypeAdapter

from ._pydantic import PydanticTypeAdapter

type NonNegativeIntStr = Annotated[
    str,
    Field(
        description="An non-negative integer stored as a string.",
        examples=["512", "024", "0"],
        pattern=r"[0-9]+",
    ),
]

NonNegativeIntStrTA: TypeAdapter[NonNegativeIntStr] = PydanticTypeAdapter(NonNegativeIntStr)
