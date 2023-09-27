from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

T = TypeVar("T")


class FeatureDetector(ABC, Generic[T]):
    """
    A detector that detects a feature.
    """

    @abstractmethod
    def find(self, store_path: Path) -> None | T:
        raise NotImplementedError

    def detect(self, store_path: Path) -> bool:
        return self.find(store_path) is not None
