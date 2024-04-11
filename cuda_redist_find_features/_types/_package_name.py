from typing import Annotated

from pydantic import TypeAdapter

from ._pydantic import PydanticFrozenField, PydanticTypeAdapter

type PackageName = Annotated[
    str,
    PydanticFrozenField(
        description="The name of a package.",
        examples=["cuda_cccl", "cuda_nvcc"],
    ),
]
PackageNameTA: TypeAdapter[PackageName] = PydanticTypeAdapter(PackageName)
