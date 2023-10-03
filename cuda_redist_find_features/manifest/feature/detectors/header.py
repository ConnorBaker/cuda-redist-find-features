from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from typing_extensions import override

from cuda_redist_find_features.manifest.feature.detectors.dir import DirDetector
from cuda_redist_find_features.manifest.feature.detectors.types import FeatureDetector
from cuda_redist_find_features.manifest.feature.detectors.utilities import cached_path_rglob
from cuda_redist_find_features.utilities import get_logger

logger = get_logger(__name__)


@dataclass
class HeaderDetector(FeatureDetector[Sequence[Path]]):
    """
    Detects the presence of headers in the `include` directory.
    """

    @override
    def find(self, store_path: Path) -> None | Sequence[Path]:
        """
        Finds paths of headers under `include` within the given Nix store path.
        """
        include_dir = DirDetector(Path("include")).find(store_path)
        if include_dir is None:
            return None

        headers = [
            header
            for header in cached_path_rglob(include_dir, "*.h*", files_only=True)
            if header.suffix in {".h", ".hh", ".hpp", ".hxx"}
        ]
        if [] != headers:
            logger.debug("Found headers: %s.", headers)
            return headers

        return None
