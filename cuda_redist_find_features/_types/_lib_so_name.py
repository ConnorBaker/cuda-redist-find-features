from typing import Annotated

from pydantic import Field, TypeAdapter

from ._pydantic import PydanticTypeAdapter

type LibSoName = Annotated[
    str,
    Field(
        description="The name of a shared object file.",
        examples=["libcuda.so", "libcuda.so.1", "libcuda.so.1.2.3"],
        pattern=r"\.so(?:\.\d+)*$",
    ),
]
LibSoNameTA: TypeAdapter[LibSoName] = PydanticTypeAdapter(LibSoName)
