import json
from collections.abc import Mapping
from pathlib import Path
from typing import Self, final

from pydantic import Field, HttpUrl

from cuda_redist_find_features._types import (
    HttpUrlTA,
    PydanticObject,
    Version,
)
from cuda_redist_find_features.manifest.feature.package import FeaturePackage
from cuda_redist_find_features.manifest.feature.release import FeatureRelease, ReleaseInfo
from cuda_redist_find_features.manifest.nvidia import NvidiaManifest
from cuda_redist_find_features.utilities import get_logger

logger = get_logger(__name__)


@final
class ManifestInfo(PydanticObject):
    name: str = Field(description="The name of the manifest.")
    url_prefix: HttpUrl = Field(description="The URL prefix for the manifest.")
    url: HttpUrl = Field(description="The URL to the manifest.")
    version: Version = Field(description="The version of the manifest.")

    @classmethod
    def of(cls, name: str, url_prefix: HttpUrl, version: Version) -> Self:
        return cls(
            name=name,
            version=version,
            url_prefix=url_prefix,
            url=HttpUrlTA.validate_strings(f"{url_prefix}/{name}"),
        )


@final
class FeatureManifest(PydanticObject):
    """
    Represents the manifest file containing releases.
    """

    manifest_info: ManifestInfo = Field(description="The manifest information.")
    releases: Mapping[str, FeatureRelease] = Field(description="The releases in the manifest.")

    def write(self, path: Path) -> None:
        """
        Writes the manifest to the given path.
        """

        with path.open("w") as f:
            json.dump(self.model_dump(mode="json"), f, indent=2, sort_keys=True)
            f.write("\n")

    @classmethod
    def of(
        cls,
        cleanup: bool,
        manifest: NvidiaManifest,
        name: str,
        url_prefix: HttpUrl,
        version: Version,
    ) -> Self:
        manifest_info = ManifestInfo.of(name=name, url_prefix=url_prefix, version=version)
        feature_releases: dict[str, FeatureRelease] = {}
        for package_name, release in manifest.releases.items():
            release_info = ReleaseInfo.of(
                release_date=manifest.release_date,
                release_label=manifest.release_label,
                release_product=manifest.release_product,
                release=release,
            )
            feature_packages = FeaturePackage.of(
                cleanup=cleanup,
                package_name=package_name,
                release=release,
                url_prefix=url_prefix,
            )
            feature_releases[package_name] = FeatureRelease(
                packages=feature_packages,
                release_info=release_info,
            )

        return cls(
            manifest_info=manifest_info,
            releases=feature_releases,
        )
