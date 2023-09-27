from pathlib import Path
from typing import Mapping, Sequence

from pydantic import BaseModel
from typing_extensions import Self

from cuda_redist_find_features.types import GpuArchitecture

from .detectors import CudaArchitecturesDetector


class FeatureCudaArchitectures(BaseModel):
    """
    Either:

    - List of architectures supported by the given libraries.
    - Mapping from subdirectory name to list of architectures supported by the libraries in that subdirectory.
    """

    __root__: Sequence[GpuArchitecture] | Mapping[Path, Sequence[GpuArchitecture]]

    @classmethod
    def of(cls, store_path: Path) -> Self:
        return cls.parse_obj(CudaArchitecturesDetector().find(store_path) or [])
