from pathlib import Path

from cuda_redist_find_features._types import Md5, PydanticFrozenField, PydanticObject, Sha256


class NvidiaPackage(PydanticObject):
    """
    Represents a single package in the manifest.

    A package is a release for a specific architecture.
    """

    relative_path: Path = PydanticFrozenField(description="The path to the package relative to the release.")
    sha256: Sha256 = PydanticFrozenField(description="The SHA256 hash of the package.")
    md5: Md5 = PydanticFrozenField(description="The MD5 hash of the package.")
    size: str = PydanticFrozenField(description="The size of the package in bytes, as a string.")
