from typing import Annotated

from pydantic import TypeAdapter
from typing_extensions import TypeAliasType

from ._pydantic import PydanticFrozenField, PydanticTypeAdapter

LibSoName = TypeAliasType(
    "LibSoName",
    Annotated[
        str,
        PydanticFrozenField(
            description="The name of a shared object file.",
            examples=["libcuda.so", "libcuda.so.1", "libcuda.so.1.2.3"],
            pattern=r"\.so(?:\.\d+)*$",
        ),
    ],
)
LibSoNameTA: TypeAdapter[LibSoName] = PydanticTypeAdapter(LibSoName)
