from typing import Self

from pydantic import model_validator

from cuda_redist_find_features.types import SFBM
from cuda_redist_find_features.version import Version


class VersionConstraint(SFBM):
    version_min: None | Version = None
    version_max: None | Version = None
    version: None | Version = None

    @model_validator(mode="after")
    def min_max_order(self) -> Self:
        if self.version_min is None or self.version_max is None or self.version_min <= self.version_max:
            return self
        raise ValueError("Invalid version constraint: version_min must be less than or equal to version_max")

    @model_validator(mode="after")
    def version_exclusivity(self) -> Self:
        if self.version is None or (self.version_min is None and self.version_max is None):
            return self
        raise ValueError("Invalid version constraint: Cannot specify both version and version_min or version_max")

    def is_satisfied_by(self, version: Version) -> bool:
        return (
            (self.version_min is None or version >= self.version_min)
            and (self.version_max is None or version <= self.version_max)
            and (self.version is None or version == self.version)
        )
