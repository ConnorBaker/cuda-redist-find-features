from __future__ import annotations

from typing import Generic, Literal, TypeAlias, TypeVar, get_args

from pydantic import Field
from pydantic.generics import GenericModel

T = TypeVar("T")

Architecture: TypeAlias = Literal[
    "linux-aarch64",
    "linux-ppc64le",
    "linux-sbsa",
    "linux-x86_64",
    "windows-x86_64",
]


class Package(GenericModel, Generic[T]):
    name: str  # This is the full name of the package, not the abbreviated name
    license: str
    version: str
    license_path: None | str = None
    linux_aarch64: None | T = Field(None, alias="linux-aarch64")
    linux_ppc64le: None | T = Field(None, alias="linux-ppc64le")
    linux_sbsa: None | T = Field(None, alias="linux-sbsa")
    linux_x86_64: None | T = Field(None, alias="linux-x86_64")
    windows_x86_64: None | T = Field(None, alias="windows-x86_64")

    def get_architectures(self) -> dict[Architecture, None | T]:
        return {arch: getattr(self, arch.replace("-", "_"), None) for arch in get_args(Architecture)}
