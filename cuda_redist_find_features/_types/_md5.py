from typing import Annotated

from pydantic import Field, TypeAdapter

from ._pydantic import PydanticTypeAdapter

type Md5 = Annotated[
    str,
    Field(
        description="An MD5 hash.",
        examples=["0123456789abcdef0123456789abcdef"],
        pattern=r"[0-9a-f]{32}",
    ),
]
Md5TA: TypeAdapter[Md5] = PydanticTypeAdapter(Md5)
