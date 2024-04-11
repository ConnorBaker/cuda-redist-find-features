from typing import Annotated

from pydantic import TypeAdapter

from ._pydantic import PydanticFrozenField, PydanticTypeAdapter

type CudaArch = Annotated[
    str,
    PydanticFrozenField(
        description="A CUDA architecture name.",
        examples=["sm_35", "sm_50", "sm_60", "sm_70", "sm_75", "sm_80", "sm_86", "sm_90a"],
        pattern=r"^sm_\d+[a-z]?$",
    ),
]
CudaArchTA: TypeAdapter[CudaArch] = PydanticTypeAdapter(CudaArch)
