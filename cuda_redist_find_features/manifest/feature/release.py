from collections.abc import Sequence
from typing import Self, final

from pydantic import Field

from cuda_redist_find_features._types import (
    PydanticObject,
    Version,
    VersionTA,
)
from cuda_redist_find_features.manifest.feature.package import FeaturePackage
from cuda_redist_find_features.manifest.nvidia import NvidiaRelease
from cuda_redist_find_features.utilities import get_logger

logger = get_logger(__name__)


@final
class ReleaseInfo(PydanticObject):
    date: None | str = Field(description="The date of the release.")
    label: None | str = Field(description="The label of the release.")
    license_path: None | str = Field(description="The path to the license file.")
    license: str = Field(description="The license of the release.")
    name: str = Field(description="The name of the release.")
    product: None | str = Field(description="The product of the release.")
    version: Version = Field(description="The version of the release.")

    @classmethod
    def of(
        cls,
        release_date: None | str,
        release_label: None | str,
        release_product: None | str,
        release: NvidiaRelease,
    ) -> Self:
        return cls(
            date=release_date,
            label=release_label,
            license_path=release.license_path,
            license=release.license,
            name=release.name,
            product=release_product,
            version=VersionTA.validate_strings(release.version),
        )


@final
class FeatureRelease(PydanticObject):
    """
    Represents the releases containing packages.
    """

    packages: Sequence[FeaturePackage] = Field(description="The packages in the release.")
    release_info: ReleaseInfo = Field(description="The release information.")
