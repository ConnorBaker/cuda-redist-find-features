from typing import Annotated

from pydantic import Field, TypeAdapter

from ._pydantic import PydanticTypeAdapter

type Sha256 = Annotated[
    str,
    Field(
        description="A SHA256 hash.",
        examples=["0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"],
        pattern=r"[0-9a-f]{64}",
    ),
]
Sha256TA: TypeAdapter[Sha256] = PydanticTypeAdapter(Sha256)
