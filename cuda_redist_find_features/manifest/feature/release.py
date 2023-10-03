from typing import Self

from pydantic import HttpUrl

from cuda_redist_find_features.manifest.feature.package import FeaturePackage
from cuda_redist_find_features.manifest.nvidia import NvidiaRelease
from cuda_redist_find_features.types import SFMRM, Platform


class FeatureRelease(SFMRM[Platform, FeaturePackage]):
    """
    Represents a release in the manifest.

    A release is a collection of packages of the same library for different architectures.
    """

    @classmethod
    def of(cls, url_prefix: HttpUrl, nvidia_release: NvidiaRelease, cleanup: bool = False) -> Self:
        return cls.model_validate(
            {
                arch: FeaturePackage.of(url_prefix, nvidia_package, cleanup)
                for arch, nvidia_package in nvidia_release.packages.items()
            }
        )
