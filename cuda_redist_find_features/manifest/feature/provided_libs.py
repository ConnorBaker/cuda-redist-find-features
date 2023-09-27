from collections.abc import Mapping, Sequence
from pathlib import Path

from pydantic import BaseModel
from typing_extensions import Self

from cuda_redist_find_features.types import LibSoName

from .detectors import ProvidedLibsDetector


class FeatureProvidedLibs(BaseModel):
    __root__: Sequence[LibSoName] | Mapping[str, Sequence[LibSoName]]

    @classmethod
    def of(cls, store_path: Path) -> Self:
        return cls.parse_obj(ProvidedLibsDetector().find(store_path) or [])
