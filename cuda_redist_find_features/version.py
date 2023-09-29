from functools import total_ordering
from typing import Annotated, Self

from typing_extensions import TypeAliasType

from .types import SFBM, SFF, validate_call

NonNegativeInt = TypeAliasType(
    "NonNegativeInt",
    Annotated[int, SFF(ge=0)],
)


@total_ordering
class Version(SFBM):
    major: NonNegativeInt
    minor: NonNegativeInt
    patch: NonNegativeInt
    build: None | NonNegativeInt = None

    def __lt__(self, other: Self) -> bool:
        self_components: list[int] = [value for _, value in self if value is not None]
        other_components: list[int] = [value for _, value in other if value is not None]
        return self_components < other_components

    @classmethod
    def parse(cls, version: str) -> Self:
        """
        Parses a version string of the form "major.minor.patch" or "major.minor.patch.build".
        """
        components = version.split(".")
        if len(components) > len(cls.model_fields):
            raise ValueError(f"Invalid version string: {version}")
        return cls(**dict(zip(cls.model_fields.keys(), map(int, components))))

    @validate_call
    def __str__(self) -> str:
        return ".".join(str(value) for _, value in self if value is not None)
