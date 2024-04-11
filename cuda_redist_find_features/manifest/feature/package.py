import logging
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Self, final

from pydantic import Field, HttpUrl, model_validator

from cuda_redist_find_features._types import (
    CudaVariantName,
    CudaVariantVersion,
    CudaVariantVersionTA,
    HttpUrlTA,
    Md5,
    NixStoreEntry,
    PackageName,
    Platform,
    PydanticObject,
    Sha256,
    SriHash,
)
from cuda_redist_find_features.manifest.feature.detectors.lib_subdirs import LibSubdirsDetector
from cuda_redist_find_features.manifest.feature.outputs import FeatureOutputs
from cuda_redist_find_features.manifest.nvidia import NvidiaPackage, NvidiaRelease
from cuda_redist_find_features.utilities import get_logger

logger = get_logger(__name__)


@final
class PackageInfo(PydanticObject):
    cuda_variant: None | CudaVariantVersion = Field(description="The CUDA variant of the release.")
    md5: Md5 = Field(description="The MD5 hash of the package.")
    name: PackageName = Field(description="The name of the package.")
    platform: Platform = Field(description="The name of the platform.")
    relative_path: Path = Field(description="The path to the package relative to the release.")
    sha256: Sha256 = Field(description="The SHA256 hash of the package.")
    size: int = Field(description="The size of the package in bytes.")

    @classmethod
    def of(
        cls,
        cuda_variant_name: None | CudaVariantName,
        package_name: PackageName,
        package: NvidiaPackage,
        platform: Platform,
    ) -> Self:
        cuda_variant_version: None | CudaVariantVersion = (
            CudaVariantVersionTA.validate_strings(cuda_variant_name.removeprefix("cuda"))
            if cuda_variant_name is not None
            else None
        )
        return cls(
            cuda_variant=cuda_variant_version,
            md5=package.md5,
            name=package_name,
            platform=platform,
            relative_path=package.relative_path,
            sha256=package.sha256,
            size=int(package.size),
        )

    def __lt__(self, other: Self) -> bool:
        return sorted([(k, v) for k, v in self], key=lambda t: t[0]) < sorted(
            [(k, v) for k, v in other], key=lambda t: t[0]
        )


@final
class NixpkgsInfo(PydanticObject):
    hash: SriHash = Field(description="The hash of the tarball.")
    lib_subdirs: Sequence[Path] = Field(description="The names of the subdirectories of `lib`.")
    nar_hash: SriHash = Field(description="The hash of the unpacked contents of the tarball.")
    outputs: FeatureOutputs = Field(description="The outputs of the package.")
    url: HttpUrl = Field(description="The URL to the tarball.")

    @classmethod
    def of(
        cls,
        cleanup: bool,
        relative_path: Path,
        sha256: Sha256,
        url_prefix: HttpUrl,
    ) -> Self:
        # Get the store path for the package.
        url = HttpUrlTA.validate_strings(f"{url_prefix}/{relative_path}")
        archive = NixStoreEntry.from_url(url, sha256)
        unpacked = archive.unpack_archive()

        if logger.getEffectiveLevel() == logging.DEBUG:
            tree_lines: list[str] = []

            def mk_tree_lines(path: Path, prefix: str = "") -> None:
                for item in sorted(path.iterdir()):
                    tree_lines.append(f"{prefix}├─ {item.name}")
                    if item.is_dir():
                        mk_tree_lines(item, prefix + "│  ")

            mk_tree_lines(unpacked.store_path)
            logger.debug("Unpacked contents of %s:\n%s", unpacked.store_path, "\n".join(tree_lines))

        # Get the features
        outputs = FeatureOutputs.of(unpacked.store_path)

        # Find subdirs of lib
        lib_subdirs: Sequence[Path] = (
            _lib_subdirs if (_lib_subdirs := LibSubdirsDetector().find(unpacked.store_path)) is not None else []
        )

        if cleanup:
            logger.debug("Cleaning up %s and %s...", archive.store_path, unpacked.store_path)
            unpacked.delete()
            archive.delete()

        return cls(
            url=url,
            hash=archive.hash,
            nar_hash=unpacked.hash,
            outputs=outputs,
            lib_subdirs=lib_subdirs,
        )

    def __lt__(self, other: Self) -> bool:
        return sorted([(k, v) for k, v in self], key=lambda t: t[0]) < sorted(
            [(k, v) for k, v in other], key=lambda t: t[0]
        )


@final
class FeaturePackage(PydanticObject):
    """
    Represents the packages.
    """

    nixpkgs_info: NixpkgsInfo = Field(description="The nixpkgs information.")
    package_info: PackageInfo = Field(description="The package information.")

    @model_validator(mode="after")
    def cuda_variant_libpath_exclusivity(self) -> Self:
        if self.package_info.cuda_variant is not None and self.nixpkgs_info.lib_subdirs != []:
            raise ValueError(
                "Invalid flattened manifest entry: Cannot specify both CUDA variant and lib subdirectories"
            )
        return self

    def __lt__(self, other: Self) -> bool:
        return sorted([(k, v) for k, v in self], key=lambda t: t[0]) < sorted(
            [(k, v) for k, v in other], key=lambda t: t[0]
        )

    @classmethod
    def of(
        cls,
        cleanup: bool,
        package_name: PackageName,
        release: NvidiaRelease,
        url_prefix: HttpUrl,
    ) -> Sequence[Self]:
        feature_packages: list[Self] = []
        for platform, maybe_packages in release.packages.items():
            # Skip non-linux platforms
            if not platform.startswith("linux"):
                continue

            # Box maybe_packages into a Mapping if it is not already one.
            match maybe_packages:
                case NvidiaPackage():
                    packages = {None: maybe_packages}
                case Mapping():
                    packages = maybe_packages
            for cuda_variant_name, package in packages.items():
                package_info = PackageInfo.of(
                    cuda_variant_name=cuda_variant_name,
                    package_name=package_name,
                    package=package,
                    platform=platform,
                )
                nixpkgs_info = NixpkgsInfo.of(
                    cleanup=cleanup,
                    relative_path=package_info.relative_path,
                    sha256=package_info.sha256,
                    url_prefix=url_prefix,
                )

                feature_packages.append(cls(nixpkgs_info=nixpkgs_info, package_info=package_info))

        feature_packages.sort()
        return feature_packages
