from collections.abc import Mapping, Sequence
from typing import final

from pydantic import Field, TypeAdapter

from cuda_redist_find_features._types import (
    CudaVariantName,
    CudaVariantVersion,
    Platform,
    PydanticMapping,
    PydanticObject,
    PydanticTypeAdapter,
)

from ._package import NvidiaPackage

# TODO: Unfortunately we cannot abstract over the fields of the release, including __pydantic_extra__.
# The most we can do is the common fields and the packages property. Check back on these bugs:
#
# - https://github.com/pydantic/pydantic/issues/8984
# - https://github.com/pydantic/pydantic/issues/9136


class _NvidiaReleaseCommon[Pkg: (NvidiaPackage, Mapping[CudaVariantName, NvidiaPackage])](PydanticObject):
    """
    Represents a release in the manifest.

    A release is a collection of packages of the same library for different architectures.
    """

    name: str = Field(description="The name of the release.")
    license: str = Field(description="The license of the release.")
    version: str = Field(description="The version of the release.")
    license_path: None | str = Field(description="The path to the license file.", default=None)

    @property
    def packages(self) -> PydanticMapping[Platform, Pkg]:
        """
        Returns a copy of the packages in the release.
        """
        return PydanticMapping[Platform, Pkg].model_validate(self.__pydantic_extra__)


@final
class NvidiaReleaseV2(_NvidiaReleaseCommon[NvidiaPackage], extra="allow"):
    __pydantic_extra__: dict[str, NvidiaPackage]  # pyright: ignore[reportIncompatibleVariableOverride]


@final
class NvidiaReleaseV3(_NvidiaReleaseCommon[Mapping[CudaVariantName, NvidiaPackage]], extra="allow"):
    cuda_variant: Sequence[CudaVariantVersion] = Field(description="The CUDA variants of the release.")
    __pydantic_extra__: dict[str, Mapping[CudaVariantName, NvidiaPackage]]  # pyright: ignore[reportIncompatibleVariableOverride]


type NvidiaRelease = NvidiaReleaseV2 | NvidiaReleaseV3
NvidiaReleaseTA: TypeAdapter[NvidiaRelease] = PydanticTypeAdapter(NvidiaRelease)
