from typing import TypeVar

from pydantic import validator
from pydantic.dataclasses import dataclass
from typing_extensions import Self

# Allows us to express a relationship between input and output type (more so than just a union type).
_NoneOrInt = TypeVar("_NoneOrInt", None, int)


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int
    build: None | int = None

    @validator("major", "minor", "patch", "build")
    def component_must_be_positive(cls, component: _NoneOrInt) -> _NoneOrInt:
        if component is not None and component < 0:
            raise ValueError(f"Invalid version component: {component} is negative")
        else:
            return component

    @classmethod
    def parse(cls, version: str) -> Self:
        """
        Parses a version string of the form "major.minor.patch" or "major.minor.patch.build".
        """
        major, minor, patch, *build = version.split(".")
        if len(build) == 0:
            return cls(major=int(major), minor=int(minor), patch=int(patch))
        elif len(build) == 1:
            return cls(major=int(major), minor=int(minor), patch=int(patch), build=int(build[0]))
        else:
            raise ValueError(f"Invalid version string: {version}")

    def __str__(self) -> str:
        if self.build is None:
            return f"{self.major}.{self.minor}.{self.patch}"
        else:
            return f"{self.major}.{self.minor}.{self.patch}.{self.build}"
