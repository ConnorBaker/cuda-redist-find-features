from pathlib import Path

from cuda_redist_find_features.types import PackageName, PydanticMapping

from .package import FeaturePackageTy
from .release import FeatureRelease


class FeatureManifest(PydanticMapping[PackageName, FeatureRelease[FeaturePackageTy]]):
    """
    Represents the manifest file containing releases.
    """

    def write(self, path: Path) -> None:
        """
        Writes the manifest to the given path.
        """
        import json

        with path.open("w") as f:
            json.dump(self.model_dump(mode="json", by_alias=True), f, indent=2, sort_keys=True)
            f.write("\n")
