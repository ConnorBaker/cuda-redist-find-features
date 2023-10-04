from collections.abc import Mapping, Sequence
from typing import Self

from cuda_redist_find_features.types import PackageId, PackageName, PydanticFrozenField
from cuda_redist_find_features.utilities import get_logger

from .package import FeaturePackage
from .package_deps_resolver import FeaturePackageDepsResolver
from .package_deps_unresolved import FeaturePackageDepsUnresolved

logger = get_logger(__name__)


class FeaturePackageDepsResolved(FeaturePackage):
    dependencies: Sequence[PackageName] | Mapping[str, Sequence[PackageName]] = PydanticFrozenField(
        description="The dependencies of the package.",
        examples=["cuda", "cudaToolkit"],
    )

    @classmethod
    def of(
        cls,
        package_id: PackageId,
        feature_package: FeaturePackageDepsUnresolved,
        dependency_resolver: FeaturePackageDepsResolver,
    ) -> Self:
        # Do lookup of feature_package dependencies in DependenciesResolver and add them to the FeaturePackage,
        # returning a FeaturePackageDepsResolved.
        platform = package_id.platform
        version = package_id.version
        lib = feature_package.needed_libs
        match lib:
            case Sequence():
                dependencies: list[PackageName] = []
                for libsoname in lib:
                    resolved_dependency = dependency_resolver.lookup_lib_provider(platform, libsoname, version)
                    if resolved_dependency is not None:
                        dependencies.append(resolved_dependency.package_name)
                return FeaturePackageDepsResolved.model_validate(
                    feature_package.model_dump() | {"dependencies": dependencies}
                )
            case Mapping():
                dependency_map: dict[str, list[PackageName]] = {}
                # TODO: Test if the subdirs are version numbers -- if so, look up the version number in the
                # dependency_resolver and use that instead of the subdir.
                for subdir, libsonames in lib.items():
                    for libsoname in libsonames:
                        resolved_dependency = dependency_resolver.lookup_lib_provider(platform, libsoname, version)
                        if resolved_dependency is not None:
                            dependency_map.setdefault(subdir, []).append(resolved_dependency.package_name)
                return FeaturePackageDepsResolved.model_validate(
                    feature_package.model_dump() | {"dependencies": dependency_map}
                )
