from typing import Annotated

from pydantic import TypeAdapter
from typing_extensions import TypeAliasType

from ._pydantic import PydanticFrozenField, PydanticTypeAdapter

PackageName = TypeAliasType(
    "PackageName",
    Annotated[
        str,
        PydanticFrozenField(
            description="The name of a package.",
            examples=["cuda_cccl", "cuda_nvcc"],
        ),
    ],
)
PackageNameTA: TypeAdapter[PackageName] = PydanticTypeAdapter(PackageName)
