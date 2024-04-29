# NOTE: Open bugs in Pydantic like https://github.com/pydantic/pydantic/issues/8984 prevent the full switch to the type
# keyword introduced in Python 3.12.
import operator
from functools import partial
from logging import Logger
from pathlib import Path
from typing import (
    Any,
    Final,
    Self,
    TypeAlias,
    cast,
)

from cuda_redist_lib.logger import get_logger
from cuda_redist_lib.manifest import get_nvidia_manifest, get_nvidia_manifest_versions
from cuda_redist_lib.pydantic import PydanticMapping, PydanticObject
from cuda_redist_lib.types import (
    CudaVariant,
    IgnoredPlatforms,
    PackageName,
    PackageNameTA,
    Platform,
    Platforms,
    RedistName,
    RedistNames,
    Sha256,
    Sha256TA,
    Version,
)
from cuda_redist_lib.utilities import mk_relative_path

logger: Final[Logger] = get_logger(__name__)


class PackageInfo(PydanticObject):
    """
    A package in the manifest, with a hash and a relative path.

    The relative path is None when it can be reconstructed from information in the index.

    A case where the relative path is non-None: TensorRT, which does not follow the usual naming convention.
    """

    sha256: Sha256
    relative_path: None | Path = None


PackageVariants: TypeAlias = PydanticMapping[None | CudaVariant, PackageInfo]

Packages: TypeAlias = PydanticMapping[Platform, PackageVariants]


class ReleaseInfo(PydanticObject):
    """
    Top-level values in the manifest from keys not prefixed with release_, augmented with the package_name.
    """

    license_path: None | Path = None
    license: None | str = None
    name: None | str = None
    version: Version

    @classmethod
    def mk(cls: type[Self], nvidia_release: dict[str, Any]) -> Self:
        """
        Creates an instance of ReleaseInfo from the provided manifest dictionary, removing the fields
        used to create the instance from the dictionary.
        """
        kwargs = {name: nvidia_release.pop(name, None) for name in ["license_path", "license", "name", "version"]}
        kwargs["license_path"] = Path(kwargs["license_path"]) if kwargs["license_path"] is not None else None
        return cls.model_validate(kwargs)


class Release(PydanticObject):
    release_info: ReleaseInfo
    packages: Packages

    @classmethod
    def mk(
        cls: type[Self],
        package_name: PackageName,
        nvidia_release: dict[str, Any],
    ) -> Self:
        release_info = ReleaseInfo.mk(nvidia_release)

        # Remove ignored platforms if they exist.
        for ignored_platform in IgnoredPlatforms:
            if ignored_platform in nvidia_release:
                del nvidia_release[ignored_platform]

        # Remove cuda_variant keys if they exist.
        if "cuda_variant" in nvidia_release:
            del nvidia_release["cuda_variant"]

        # Check that the keys are valid.
        key_set = set(nvidia_release.keys())
        if (key_set - Platforms) != set():
            raise RuntimeError(f"Expected keys to be in {Platforms}, got {key_set}")
        else:
            key_set = cast(set[Platform], key_set)

        packages: dict[Platform, PackageVariants] = {
            platform: mk_package_hashes(
                package_name,
                release_info,
                platform,
                nvidia_release.pop(platform),
            )
            for platform in key_set
        }

        if nvidia_release != {}:
            raise RuntimeError(
                f"Expected release for {release_info} to be empty after processing, got {nvidia_release}"
            )

        return cls.model_validate({"release_info": release_info, "packages": packages})


Manifest: TypeAlias = PydanticMapping[PackageName, Release]

VersionedManifests: TypeAlias = PydanticMapping[Version, Manifest]

Index: TypeAlias = PydanticMapping[RedistName, VersionedManifests]


def mk_package_hashes(
    package_name: PackageName,
    release_info: ReleaseInfo,
    platform: Platform,
    nvidia_package: dict[str, Any],
) -> PackageVariants:
    """
    Creates an instance of PackageInfo from the provided manifest dictionary, removing the fields
    used to create the instance from the dictionary.
    NOTE: Because the keys may be prefixed with "cuda", indicating multiple packages, we return a sequence of
    PackageInfo instances.
    """
    # Two cases: either our keys are package keys, or they're boxed inside an object mapping a prefixed CUDA version
    # (e.g., "cuda11") to the package keys.
    all_cuda_keys: bool = all(key.startswith("cuda") for key in nvidia_package.keys())
    any_cuda_keys: bool = any(key.startswith("cuda") for key in nvidia_package.keys())

    if any_cuda_keys and not all_cuda_keys:
        raise RuntimeError(
            f"Expected all package keys to start with 'cuda' or none to start with 'cuda', got {nvidia_package.keys()}"
        )

    packages: dict[None | str, Any] = {None: nvidia_package} if not any_cuda_keys else nvidia_package  # type: ignore
    infos: dict[None | CudaVariant, PackageInfo] = {}
    for cuda_variant_name in set(packages.keys()):
        nvidia_package = packages.pop(cuda_variant_name)
        sha256 = Sha256TA.validate_strings(nvidia_package.pop("sha256"))

        # Verify that we can compute the correct relative path before throwing it away.
        actual_relative_path = Path(nvidia_package.pop("relative_path"))
        expected_relative_path = mk_relative_path(package_name, platform, release_info.version, cuda_variant_name)
        package_info: PackageInfo
        if actual_relative_path != expected_relative_path:
            # TensorRT will fail this check because it doesn't follow the usual naming convention.
            if release_info.name != "NVIDIA TensorRT":
                logger.info("Expected relative path to be %s, got %s", expected_relative_path, actual_relative_path)
            package_info = PackageInfo.model_validate({"sha256": sha256, "relative_path": actual_relative_path})
        else:
            package_info = PackageInfo.model_validate({"sha256": sha256, "relative_path": None})

        infos[cuda_variant_name] = package_info
    return PackageVariants.model_validate(infos)


def mk_manifest(redist_name: RedistName, version: Version, nvidia_manifest: None | dict[str, Any] = None) -> Manifest:
    if nvidia_manifest is None:
        nvidia_manifest = get_nvidia_manifest(redist_name, version)

    for key in map(partial(operator.add, "release_"), ["date", "label", "product"]):
        if key in nvidia_manifest:
            del nvidia_manifest[key]

    releases: dict[str, Release] = {
        package_name: release
        for package_name in map(PackageNameTA.validate_strings, set(nvidia_manifest.keys()))
        # Don't include releases for packages that have no packages for the platforms we care about.
        if len((release := Release.mk(package_name, nvidia_manifest.pop(package_name))).packages) != 0
    }

    if nvidia_manifest != {}:
        raise RuntimeError(f"Expected manifest for {redist_name} to be empty after processing, got {nvidia_manifest}")

    return Manifest.model_validate(releases)


def mk_index() -> Index:
    return Index.model_validate({
        redist_name: {
            version: mk_manifest(redist_name, version) for version in get_nvidia_manifest_versions(redist_name)
        }
        for redist_name in RedistNames
    })
