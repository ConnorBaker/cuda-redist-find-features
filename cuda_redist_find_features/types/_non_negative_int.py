from typing import Annotated

from pydantic import TypeAdapter
from typing_extensions import TypeAliasType

from ._pydantic import PydanticFrozenField, PydanticTypeAdapter

NonNegativeInt = TypeAliasType(
    "NonNegativeInt",
    Annotated[int, PydanticFrozenField(ge=0)],
)

NonNegativeIntTA: TypeAdapter[NonNegativeInt] = PydanticTypeAdapter(NonNegativeInt)
