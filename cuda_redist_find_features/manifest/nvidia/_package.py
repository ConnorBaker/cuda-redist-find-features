from pathlib import Path
from typing import final

from pydantic import Field

from cuda_redist_find_features._types import Md5, PydanticObject, Sha256


@final
class NvidiaPackage(PydanticObject):
    """
    Represents a single package in the manifest.

    A package is a release for a specific architecture.
    """

    relative_path: Path = Field(description="The path to the package relative to the release.")
    sha256: Sha256 = Field(description="The SHA256 hash of the package.")
    md5: Md5 = Field(description="The MD5 hash of the package.")
    size: str = Field(description="The size of the package in bytes, as a string.")
