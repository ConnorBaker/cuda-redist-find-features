from typing import TypeVar

from pydantic import validator
from pydantic.dataclasses import dataclass

from cuda_redist_find_features.version import Version

# Allows us to express a relationship between input and output type (more so than just a union type).
_NoneOrVersion = TypeVar("_NoneOrVersion", None, Version)


@dataclass(frozen=True, order=True)
class VersionConstraint:
    version_min: None | Version = None
    version_max: None | Version = None
    version: None | Version = None

    @validator("version_max")
    def min_max_order(
        cls,
        version_max: _NoneOrVersion,
        values: dict[str, None | Version],
    ) -> _NoneOrVersion:
        version_min = values.get("version_min")
        if version_min is not None and version_max is not None and version_min > version_max:
            raise ValueError("Invalid version constraint: version_min must be less than or equal to version_max")
        else:
            return version_max

    @validator("version")
    def version_exclusivity(
        cls,
        version: _NoneOrVersion,
        values: dict[str, None | Version],
    ) -> _NoneOrVersion:
        version_min = values.get("version_min")
        version_max = values.get("version_max")
        if version is not None and (version_min is not None or version_max is not None):
            raise ValueError("Invalid version constraint: Cannot specify both version and version_min or version_max")
        else:
            return version

    def is_satisfied_by(self, version: Version) -> tuple[bool, str]:
        if self.version is not None:
            sat = version == self.version
            return sat, f"version {version} {'is' if sat else 'is not'} exactly {self.version}"

        # Recall that version is exclusive with version_min and version_max -- so we handle it in a separate
        # case.
        if self.version_min is not None and self.version_max is not None:
            sat = self.version_min <= version <= self.version_max
            return (
                sat,
                f"version {version} {'is' if sat else 'is not'} between {self.version_min} and {self.version_max}",
            )

        elif self.version_min is not None:
            sat = version >= self.version_min
            return sat, f"version {version} is {'greater than or equal to' if sat else 'less than'} {self.version_min}"

        elif self.version_max is not None:
            sat = version <= self.version_max
            return sat, f"version {version} is {'less than or equal to' if sat else 'greater than'} {self.version_max}"

        else:
            return True, f"version {version} is not constrained"
