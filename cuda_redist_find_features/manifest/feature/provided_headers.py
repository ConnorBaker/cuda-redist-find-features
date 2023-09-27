from pathlib import Path
from typing import Sequence

from pydantic import BaseModel
from typing_extensions import Self

from .detectors import HeaderDetector


class FeatureProvidedHeaders(BaseModel):
    __root__: Sequence[Path]

    @classmethod
    def of(cls, store_path: Path) -> Self:
        return cls.parse_obj(
            [header.relative_to(store_path / "include") for header in HeaderDetector().find(store_path) or []]
        )
