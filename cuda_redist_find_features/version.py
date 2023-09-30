from collections.abc import Mapping
from functools import total_ordering
from typing import Annotated, Any

from pydantic import model_serializer, model_validator
from typing_extensions import TypeAliasType

from .types import SFBM, SFF

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

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        self_components: list[int] = [value for _, value in self if value is not None]
        other_components: list[int] = [value for _, value in other if value is not None]
        return self_components < other_components

    @model_validator(mode="before")
    @classmethod
    def _from_string(cls, value: str | Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Parses a version string of the form "major.minor.patch" or "major.minor.patch.build".
        """
        if isinstance(value, Mapping):
            return value

        components = value.split(".")
        if len(components) > len(cls.model_fields):
            raise ValueError(f"Invalid version string: {value}")
        return dict(zip(cls.model_fields.keys(), map(int, components)))

    @model_serializer(mode="plain")
    def __str__(self) -> str:
        return ".".join(str(value) for _, value in self if value is not None)
