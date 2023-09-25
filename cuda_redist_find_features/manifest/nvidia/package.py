from pathlib import Path

from pydantic import BaseModel

from cuda_redist_find_features.types import Md5, Sha256


class NvidiaPackage(BaseModel):
    """
    Represents a single package in the manifest.

    A package is a release for a specific architecture.
    """

    relative_path: Path
    sha256: Sha256
    md5: Md5
    size: str
