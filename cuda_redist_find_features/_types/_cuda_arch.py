from typing import Annotated

from pydantic import Field, TypeAdapter

from ._pydantic import PydanticTypeAdapter

type CudaArch = Annotated[
    str,
    Field(
        description="A CUDA architecture name.",
        examples=["sm_35", "sm_50", "sm_60", "sm_70", "sm_75", "sm_80", "sm_86", "sm_90a"],
        pattern=r"^sm_\d+[a-z]?$",
    ),
]
CudaArchTA: TypeAdapter[CudaArch] = PydanticTypeAdapter(CudaArch)
