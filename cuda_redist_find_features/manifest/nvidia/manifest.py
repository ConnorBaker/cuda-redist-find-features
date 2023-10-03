from cuda_redist_find_features.manifest.nvidia.release import NvidiaRelease
from cuda_redist_find_features.types import SFBM, SFF, SFMRM, PackageName


class NvidiaManifest(SFBM, extra="allow"):
    """
    Represents the manifest file containing releases.
    """

    release_date: None | str = SFF(description="The date of the release.", default=None)
    release_label: None | str = SFF(description="The label of the release.", default=None)
    release_product: None | str = SFF(description="The product of the release.", default=None)
    __pydantic_extra__: dict[str, NvidiaRelease]  # pyright: ignore[reportIncompatibleVariableOverride]

    @property
    def releases(self) -> SFMRM[PackageName, NvidiaRelease]:
        """
        Returns a copy of the releases in the manifest.
        """
        return SFMRM[PackageName, NvidiaRelease].model_validate(self.__pydantic_extra__)
