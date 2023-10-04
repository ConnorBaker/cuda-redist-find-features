from cuda_redist_find_features.types import Platform, PydanticMapping

from .package import FeaturePackageTy


class FeatureRelease(PydanticMapping[Platform, FeaturePackageTy]):
    """
    Represents a release in the manifest.

    A release is a collection of packages of the same library for different architectures.
    """
