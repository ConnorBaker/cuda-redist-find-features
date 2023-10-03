from pathlib import Path

from cuda_redist_find_features.manifest.feature.release import FeatureRelease
from cuda_redist_find_features.types import SFMRM, PackageName


class FeatureManifest(SFMRM[PackageName, FeatureRelease]):
    """
    Represents the manifest file containing releases.
    """

    def write(self, path: Path) -> None:
        """
        Writes the manifest to the given path.
        """
        with path.open("w") as f:
            f.write(self.model_dump_json(by_alias=True, exclude_none=True, indent=2))
            f.write("\n")
            f.flush()
