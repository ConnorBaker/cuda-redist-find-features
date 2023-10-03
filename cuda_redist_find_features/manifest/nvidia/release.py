from cuda_redist_find_features.manifest.nvidia.package import NvidiaPackage
from cuda_redist_find_features.types import SFBM, SFF, SFMRM, Platform


class NvidiaRelease(SFBM, extra="allow"):
    """
    Represents a release in the manifest.

    A release is a collection of packages of the same library for different architectures.
    """

    name: str = SFF(description="The name of the release.")
    license: str = SFF(description="The license of the release.")
    version: str = SFF(description="The version of the release.")
    license_path: None | str = SFF(description="The path to the license file.", default=None)
    __pydantic_extra__: dict[str, NvidiaPackage]  # pyright: ignore[reportIncompatibleVariableOverride]

    @property
    def packages(self) -> SFMRM[Platform, NvidiaPackage]:
        """
        Returns a copy of the packages in the release.
        """
        return SFMRM[Platform, NvidiaPackage].model_validate(self.__pydantic_extra__)
