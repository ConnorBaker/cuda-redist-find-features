from typing import Annotated

from pydantic import Field, TypeAdapter

from ._pydantic import PydanticTypeAdapter

type CudaVariantName = Annotated[
    str,
    Field(
        description="A CUDA variant name.",
        examples=["11", "12"],
        pattern=r"^cuda1[1-2]$",
    ),
]
CudaVariantNameTA: TypeAdapter[CudaVariantName] = PydanticTypeAdapter(CudaVariantName)
