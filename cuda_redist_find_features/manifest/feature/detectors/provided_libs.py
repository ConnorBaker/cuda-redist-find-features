import logging
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from typing_extensions import override

from cuda_redist_find_features.types import LibSoName

from .groupable_feature_detector import GroupableFeatureDetector


@dataclass
class ProvidedLibsDetector(GroupableFeatureDetector[LibSoName]):
    """
    Either:

    - List of libs provided by the given libraries.
    - Mapping from subdirectory name to list of libs provided by the libraries in that subdirectory.
    """

    dir: Path = Path("lib")
    ignored_dirs: set[Path] = field(default_factory=lambda: set(map(Path, ("stubs", "cmake", "Win32", "x64"))))

    @staticmethod
    @override
    def path_feature_detector(path: Path) -> set[LibSoName]:
        """
        Returns the soname of the given library.

        The value is equivalent to the following bash snippet:

        ```console
        $ patchelf --print-soname ./libcusolver/lib/libcusolver.so
        libcusolver.so.11
        ```
        """
        logging.debug(f"Running patchelf --print-soname on {path}...")
        start_time = time.time()
        result = subprocess.run(
            ["patchelf", "--print-soname", path],
            capture_output=True,
            check=True,
        )
        end_time = time.time()
        logging.debug(f"Ran patchelf --print-soname on {path} in {end_time - start_time} seconds.")
        lib_so_name: LibSoName = LibSoName(result.stdout.decode("utf-8").strip())
        logging.debug(f"Lib soname: {lib_so_name}")
        return set((lib_so_name,))

    @staticmethod
    @override
    def path_filter(path: Path) -> bool:
        return path.suffix == ".so"

    @override
    def find(self, store_path: Path) -> None | list[LibSoName] | dict[str, list[LibSoName]]:
        logging.debug(f"Getting needed libs for {store_path}...")
        start_time = time.time()
        ret = super().find(store_path)
        end_time = time.time()
        logging.debug(f"Got needed libs for {store_path} in {end_time - start_time} seconds: {ret}.")
        return ret
