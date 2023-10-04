from collections.abc import Mapping, Sequence
from typing import TypeVar

from pydantic.alias_generators import to_camel

from cuda_redist_find_features.manifest.feature.outputs import FeatureOutputs
from cuda_redist_find_features.types import (
    CudaArch,
    LibSoName,
    PydanticFrozenField,
    PydanticObject,
)
from cuda_redist_find_features.utilities import get_logger

logger = get_logger(__name__)


class FeaturePackage(PydanticObject, alias_generator=to_camel):
    """
    Describes the different features a package can have.

    A package is a release for a specific architecture.
    """

    outputs: FeatureOutputs = PydanticFrozenField(
        description="The Nix outputs of the package.",
        examples=["lib", "dev", "static"],
    )
    cuda_architectures: Sequence[CudaArch] | Mapping[str, Sequence[CudaArch]] = PydanticFrozenField(
        description=(
            """
            The CUDA architectures supported by the package.
            This is either a list of architectures or a mapping from subdirectory name to list of architectures.
            """
        ),
    )
    provided_libs: Sequence[LibSoName] | Mapping[str, Sequence[LibSoName]] = PydanticFrozenField(
        description=(
            """
            The libraries provided by the package.
            This is either a list of libraries or a mapping from subdirectory name to list of libraries.
            """
        ),
    )
    needed_libs: Sequence[LibSoName] | Mapping[str, Sequence[LibSoName]] = PydanticFrozenField(
        description=(
            """
            The libraries needed by the package.
            This is either a list of libraries or a mapping from subdirectory name to list of libraries.
            """
        ),
    )


FeaturePackageTy = TypeVar("FeaturePackageTy", bound=FeaturePackage)
