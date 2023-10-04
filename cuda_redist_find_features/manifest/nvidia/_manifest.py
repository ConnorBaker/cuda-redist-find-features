from cuda_redist_find_features.types import PackageName, PydanticFrozenField, PydanticMapping, PydanticObject

from ._release import NvidiaRelease


class NvidiaManifest(PydanticObject, extra="allow"):
    """
    Represents the manifest file containing releases.
    """

    release_date: None | str = PydanticFrozenField(description="The date of the release.", default=None)
    release_label: None | str = PydanticFrozenField(description="The label of the release.", default=None)
    release_product: None | str = PydanticFrozenField(description="The product of the release.", default=None)
    __pydantic_extra__: dict[str, NvidiaRelease]  # pyright: ignore[reportIncompatibleVariableOverride]

    @property
    def releases(self) -> PydanticMapping[PackageName, NvidiaRelease]:
        """
        Returns a copy of the releases in the manifest.
        """
        return PydanticMapping[PackageName, NvidiaRelease].model_validate(self.__pydantic_extra__)
