from pydantic import Field, TypeAdapter

from cuda_redist_find_features._types import (
    PackageName,
    PydanticMapping,
    PydanticObject,
    PydanticTypeAdapter,
)

from ._release import NvidiaReleaseV2, NvidiaReleaseV3


class _NvidiaManifestCommon[Rel: (NvidiaReleaseV2, NvidiaReleaseV3)](PydanticObject, extra="allow"):
    """
    Represents the manifest file containing releases.
    """

    release_date: None | str = Field(description="The date of the release.", default=None)
    release_label: None | str = Field(description="The label of the release.", default=None)
    release_product: None | str = Field(description="The product of the release.", default=None)

    __pydantic_extra__: dict[str, Rel]  # pyright: ignore[reportIncompatibleVariableOverride]

    @property
    def releases(self) -> PydanticMapping[PackageName, Rel]:
        """
        Returns a copy of the releases in the manifest.
        """
        return PydanticMapping[PackageName, Rel].model_validate(self.__pydantic_extra__)


class NvidiaManifestV2(_NvidiaManifestCommon[NvidiaReleaseV2], extra="allow"):
    pass


class NvidiaManifestV3(_NvidiaManifestCommon[NvidiaReleaseV3], extra="allow"):
    pass


type NvidiaManifest = NvidiaManifestV2 | NvidiaManifestV3
NvidiaManifestTA: TypeAdapter[NvidiaManifest] = PydanticTypeAdapter(NvidiaManifest)
