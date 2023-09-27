from collections.abc import Mapping, Sequence
from pathlib import Path

from pydantic import BaseModel
from typing_extensions import Self

from cuda_redist_find_features.types import LibSoName

from .detectors import NeededLibsDetector


class FeatureNeededLibs(BaseModel):
    __root__: Sequence[LibSoName] | Mapping[Path, Sequence[LibSoName]]

    @classmethod
    def of(cls, store_path: Path) -> Self:
        return cls.parse_obj(NeededLibsDetector().find(store_path) or [])
