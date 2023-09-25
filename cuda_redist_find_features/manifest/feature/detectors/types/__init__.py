from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FeatureDetector:
    """
    A detector that detects a feature.
    """

    @abstractmethod
    def detect(self, tree: Path) -> bool:
        raise NotImplementedError
