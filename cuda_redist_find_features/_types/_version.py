from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter, dataclasses, model_serializer, model_validator

from ._non_negative_int_str import NonNegativeIntStr
from ._pydantic import model_config


@dataclasses.dataclass(frozen=True, order=True, slots=True, config=model_config)
class Version:
    major: NonNegativeIntStr
    minor: NonNegativeIntStr
    patch: None | NonNegativeIntStr = None
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
        min_num_components = 2
        max_num_components = 4
        if min_num_components <= num_components <= max_num_components:
            return dict(zip(("major", "minor", "patch", "build"), components))

        raise ValueError(
            f"Version string {value} must have between {min_num_components} and {max_num_components} components (has"
            + f" {num_components})."
        )

    @model_serializer(mode="plain")
    def __str__(self) -> str:
        return ".".join(
            component for component in (self.major, self.minor, self.patch, self.build) if component is not None
        )


# See note on PydanticTypeAdapter on why we cannot pass a config.
VersionTA: TypeAdapter[Version] = TypeAdapter(Version)
