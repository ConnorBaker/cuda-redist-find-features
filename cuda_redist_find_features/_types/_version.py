from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter, dataclasses, model_serializer, model_validator

from ._non_negative_int_str import NonNegativeIntStr
from ._pydantic import model_config


@dataclasses.dataclass(frozen=True, order=True, slots=True, config=model_config)
class Version:
    major: NonNegativeIntStr
    minor: NonNegativeIntStr
    patch: NonNegativeIntStr
    build: None | NonNegativeIntStr = None

    @model_validator(mode="before")
    @classmethod
    def _from_string(cls, value: str | Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Parses a version string of the form "major.minor.patch" or "major.minor.patch.build".
        """
        if isinstance(value, Mapping):
            return value

        components = value.split(".")
        num_components = len(components)
        min_num_components = 3
        max_num_components = 4
        if num_components < min_num_components or max_num_components < num_components:
            raise ValueError(f"Invalid version string: {value}")
        return {
            "major": components[0],
            "minor": components[1],
            "patch": components[2],
            "build": components[3] if num_components == max_num_components else None,
        }

    @model_serializer(mode="plain")
    def __str__(self) -> str:
        return ".".join(
            component for component in (self.major, self.minor, self.patch, self.build) if component is not None
        )


# See note on PydanticTypeAdapter on why we cannot pass a config.
VersionTA: TypeAdapter[Version] = TypeAdapter(Version)
