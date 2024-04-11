from typing import Annotated

from pydantic import Field, TypeAdapter

from ._pydantic import PydanticTypeAdapter

type CudaVariantVersion = Annotated[
    str,
    Field(
        description="A CUDA variant version.",
        examples=["11", "12"],
        pattern=r"^1[1-2]$",
    ),
]
CudaVariantVersionTA: TypeAdapter[CudaVariantVersion] = PydanticTypeAdapter(CudaVariantVersion)
