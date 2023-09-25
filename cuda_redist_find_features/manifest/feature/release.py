from typing import Mapping

from pydantic import BaseModel, HttpUrl
from typing_extensions import Self

from cuda_redist_find_features.types import Architecture

from ..nvidia import NvidiaRelease
from .package import FeaturePackage


class FeatureRelease(BaseModel):
    """
    Represents a release in the manifest.

    A release is a collection of packages of the same library for different architectures.

    Beyond the fields provided as properties, the package may also have the following fields,
    depending on the architectures supported by the package:

    - `linux-aarch64`
    - `linux-ppc64le`
    - `linux-sbsa`
    - `linux-x86_64`
    - `windows-x86_64`
    """

    __root__: Mapping[Architecture, FeaturePackage]

    @classmethod
    def of(cls, url_prefix: HttpUrl, nvidia_release: NvidiaRelease, cleanup: bool = False) -> Self:
        return cls.parse_obj(
            {
                arch: FeaturePackage.of(url_prefix, nvidia_package, cleanup)
                for arch, nvidia_package in nvidia_release.packages().items()
            }
        )

    def packages(self) -> dict[Architecture, FeaturePackage]:
        """
        Returns a mapping of architecture to package.
        """
        return {arch: package for arch, package in self.__root__.items()}
