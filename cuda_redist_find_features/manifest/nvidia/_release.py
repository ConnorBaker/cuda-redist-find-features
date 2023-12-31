from cuda_redist_find_features.types import Platform, PydanticFrozenField, PydanticMapping, PydanticObject

from ._package import NvidiaPackage


class NvidiaRelease(PydanticObject, extra="allow"):
    """
    Represents a release in the manifest.

    A release is a collection of packages of the same library for different architectures.
    """

    name: str = PydanticFrozenField(description="The name of the release.")
    license: str = PydanticFrozenField(description="The license of the release.")
    version: str = PydanticFrozenField(description="The version of the release.")
    license_path: None | str = PydanticFrozenField(description="The path to the license file.", default=None)
    __pydantic_extra__: dict[str, NvidiaPackage]  # pyright: ignore[reportIncompatibleVariableOverride]

    @property
    def packages(self) -> PydanticMapping[Platform, NvidiaPackage]:
        """
        Returns a copy of the packages in the release.
        """
        return PydanticMapping[Platform, NvidiaPackage].model_validate(self.__pydantic_extra__)
