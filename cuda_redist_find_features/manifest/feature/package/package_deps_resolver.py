# NOTE: Each mapping should be unique; NVIDIA doesn't follow SemVer for their library names, though they do specifically
# link against libsonames with versions in them.

# Need a list of well-known libraries and their versions -- like those typically provided by stdenv that we don't need
# to worry about.

from collections.abc import Mapping, Sequence
from itertools import chain
from pathlib import Path
from typing import Self, TypeAlias

from cuda_redist_find_features._types import LibSoName, PackageId, Platform, PydanticMapping, Version
from cuda_redist_find_features.utilities import get_logger

from .package import FeaturePackage

logger = get_logger(__name__)

_FeaturePackageDepsResolverPydanticTy: TypeAlias = PydanticMapping[
    Platform,
    Mapping[
        LibSoName,
        Mapping[
            Version,
            PackageId,
        ],
    ],
]

_FeaturePackageDepsResolverMappingTy: TypeAlias = Mapping[
    Platform,
    Mapping[
        LibSoName,
        Mapping[
            Version,
            PackageId,
        ],
    ],
]

_FeaturePackageDepsResolverDictTy: TypeAlias = dict[
    Platform,
    dict[
        LibSoName,
        dict[
            Version,
            PackageId,
        ],
    ],
]


def _lookup_lib_provider(
    mapping: _FeaturePackageDepsResolverMappingTy
    | _FeaturePackageDepsResolverPydanticTy
    | _FeaturePackageDepsResolverDictTy,
    platform: Platform,
    libsoname: LibSoName,
    version: Version,
    logging: bool = True,
) -> None | PackageId:
    try:
        # TODO: Even if the version number doesn't match exactly, we should still try to use it.
        package_id = mapping[platform][libsoname][version]
        if logging:
            logger.info("Found dependency %s -> %s -> %s -> %s", platform, libsoname, version, package_id)
        return package_id
    except KeyError:
        if logging:
            logger.warning("No dependency found for %s -> %s -> %s", platform, libsoname, version)
        return None


def _transform(package_id: PackageId, feature_package: FeaturePackage) -> _FeaturePackageDepsResolverMappingTy:
    lib = feature_package.provided_libs
    return {
        package_id.platform: {
            libsoname: {package_id.version: package_id}
            for libsoname in (lib if isinstance(lib, Sequence) else set(chain.from_iterable(lib.values())))
        }
    }


class FeaturePackageDepsResolver(_FeaturePackageDepsResolverPydanticTy):
    def lookup_lib_provider(self, platform: Platform, libsoname: LibSoName, version: Version) -> None | PackageId:
        return _lookup_lib_provider(self, platform, libsoname, version)

    def bulk_add_lib_provider(self, items: Mapping[PackageId, FeaturePackage]) -> Self:
        # Because .model_copy doesn't work with nested mappings, we have to do this manually.
        # Start by copying the current object.
        new: _FeaturePackageDepsResolverDictTy = {
            platform: {
                libsoname: {version: package_id for version, package_id in versions.items()}
                for libsoname, versions in libsonames.items()
            }
            for platform, libsonames in self.items()
        }
        for package_id, feature_package in items.items():
            update = _transform(package_id, feature_package)
            for platform, libsonames in update.items():
                new.setdefault(platform, {})
                for libsoname, versions in libsonames.items():
                    new[platform].setdefault(libsoname, {})
                    for version, _package_id in versions.items():  # Same as package_id
                        # Check if the entry already exists in the batched update
                        # This is akin to looking within the transaction log of an atomic update
                        # in a database.
                        # If the entry doesn't exist in the batched update, check if it exists in the current
                        # object.
                        current_package_id = _lookup_lib_provider(new, platform, libsoname, version, logging=False)
                        if current_package_id is not None:
                            if current_package_id == package_id:
                                logger.debug(
                                    "Entry %s -> %s -> %s -> %s exists; skipping",
                                    platform,
                                    libsoname,
                                    version,
                                    package_id,
                                )
                            else:
                                logger.error(
                                    "Entry %s -> %s -> %s -> %s exists; replacing value with %s",
                                    platform,
                                    libsoname,
                                    version,
                                    current_package_id,
                                    package_id,
                                )
                        else:
                            logger.debug(
                                "Adding entry %s -> %s -> %s -> %s",
                                platform,
                                libsoname,
                                version,
                                package_id,
                            )
                        new[platform][libsoname][version] = package_id

        return self.model_validate(new)

    def add_lib_provider(self, package_id: PackageId, feature_package: FeaturePackage) -> Self:
        return self.bulk_add_lib_provider({package_id: feature_package})

    def write(self, path: Path) -> None:
        """
        Writes the dependency db to the given path.
        """
        import json

        with path.open("w+") as f:
            json.dump(self.model_dump(mode="json", by_alias=True), f, indent=2, sort_keys=True)
            f.write("\n")
