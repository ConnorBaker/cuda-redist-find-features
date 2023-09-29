import logging
import subprocess
import time
from collections.abc import Mapping, Sequence, Set
from dataclasses import dataclass, field
from pathlib import Path

from typing_extensions import override

from cuda_redist_find_features.types import LibSoName, LibSoNameTA

from .groupable_feature_detector import GroupableFeatureDetector


@dataclass
class NeededLibsDetector(GroupableFeatureDetector[LibSoName]):
    """
    Either:

    - List of libs needed by the given libraries.
    - Mapping from subdirectory name to list of libs needed by the libraries in that subdirectory.
    """

    dir: Path = Path("lib")
    ignored_dirs: Set[Path] = field(default_factory=lambda: set(map(Path, ("stubs", "cmake", "Win32", "x64"))))

    @staticmethod
    @override
    def path_feature_detector(path: Path) -> Set[LibSoName]:
        """
        Returns a values equivalent to the following bash snippet:

        ```console
        $ patchelf --print-needed ./libcusolver/lib/libcusolver.so
        libdl.so.2
        libcublas.so.11
        libcublasLt.so.11
        librt.so.1
        libpthread.so.0
        libm.so.6
        libgcc_s.so.1
        libc.so.6
        ld-linux-x86-64.so.2
        ```
        """
        logging.debug(f"Running patchelf --print-needed on {path}...")
        start_time = time.time()
        result = subprocess.run(
            ["patchelf", "--print-needed", path],
            capture_output=True,
            check=True,
        )
        end_time = time.time()
        logging.debug(f"Ran patchelf --print-needed on {path} in {end_time - start_time} seconds.")
        libs_needed: set[LibSoName] = {
            LibSoNameTA.validate_python(name) for name in result.stdout.decode("utf-8").splitlines() if name
        }
        logging.debug(f"Libs needed: {libs_needed}")
        return libs_needed

    @staticmethod
    @override
    def path_filter(path: Path) -> bool:
        return path.suffix == ".so"

    @override
    def find(self, store_path: Path) -> None | Sequence[LibSoName] | Mapping[str, Sequence[LibSoName]]:
        logging.debug(f"Getting needed libs for {store_path}...")
        start_time = time.time()
        ret = super().find(store_path)
        end_time = time.time()
        logging.debug(f"Got needed libs for {store_path} in {end_time - start_time} seconds: {ret}.")
        return ret
