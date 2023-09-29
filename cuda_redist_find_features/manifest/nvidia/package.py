from pathlib import Path

from cuda_redist_find_features.types import SFBM, SFF, Md5, Sha256


class NvidiaPackage(SFBM):
    """
    Represents a single package in the manifest.

    A package is a release for a specific architecture.
    """

    relative_path: Path = SFF(description="The path to the package relative to the release.")
    sha256: Sha256 = SFF(description="The SHA256 hash of the package.")
    md5: Md5 = SFF(description="The MD5 hash of the package.")
    size: str = SFF(description="The size of the package in bytes, as a string.")
