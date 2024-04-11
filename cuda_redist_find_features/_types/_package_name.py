from typing import Annotated

from pydantic import Field, TypeAdapter

from ._pydantic import PydanticTypeAdapter

type PackageName = Annotated[
    str,
    Field(
        description="The name of a package.",
        examples=["cuda_cccl", "cuda_nvcc"],
    ),
]
PackageNameTA: TypeAdapter[PackageName] = PydanticTypeAdapter(PackageName)
