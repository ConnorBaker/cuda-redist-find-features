from typing import Annotated

from pydantic import TypeAdapter
from typing_extensions import TypeAliasType

from ._pydantic import PydanticFrozenField, PydanticTypeAdapter

Sha256 = TypeAliasType(
    "Sha256",
    Annotated[
        str,
        PydanticFrozenField(
            description="A SHA256 hash.",
            examples=["0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"],
            pattern=r"[0-9a-f]{64}",
        ),
    ],
)
Sha256TA: TypeAdapter[Sha256] = PydanticTypeAdapter(Sha256)
