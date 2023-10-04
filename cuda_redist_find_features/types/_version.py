from collections.abc import Mapping
from functools import partial
from operator import is_not
from typing import Any

from pydantic import TypeAdapter, dataclasses, model_serializer, model_validator

from ._non_negative_int import NonNegativeInt
from ._pydantic import model_config


@dataclasses.dataclass(frozen=True, order=True, slots=True, config=model_config)
class Version:
    major: NonNegativeInt
    minor: NonNegativeInt
    patch: NonNegativeInt
    build: None | NonNegativeInt = None

    @model_validator(mode="before")
    @classmethod
    def _from_string(cls, value: str | Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Parses a version string of the form "major.minor.patch" or "major.minor.patch.build".
        """
        if isinstance(value, Mapping):
            return value

        components = value.split(".")
        min_num_components = 3
        max_num_components = 4
        if len(components) < min_num_components or max_num_components < len(components):
            raise ValueError(f"Invalid version string: {value}")
        return {
            "major": int(components[0]),
            "minor": int(components[1]),
            "patch": int(components[2]),
            "build": int(components[3]) if len(components) == max_num_components else None,
        }

    @model_serializer(mode="plain")
    def __str__(self) -> str:
        return ".".join(map(str, filter(partial(is_not, None), (self.major, self.minor, self.patch, self.build))))


# See note on PydanticTypeAdapter on why we cannot pass a config.
VersionTA: TypeAdapter[Version] = TypeAdapter(Version)
