import logging
import re
import subprocess
import time
from collections.abc import Mapping, Sequence, Set
from dataclasses import dataclass, field
from pathlib import Path

from typing_extensions import override

from cuda_redist_find_features.types import CudaArch, CudaArchTA

from .groupable_feature_detector import GroupableFeatureDetector


@dataclass
class CudaArchitecturesDetector(GroupableFeatureDetector[CudaArch]):
    """
    Either:

    - List of architectures supported by the given libraries.
    - Mapping from subdirectory name to list of architectures supported by the libraries in that subdirectory.
    """

    dir: Path = Path("lib")
    ignored_dirs: Set[Path] = field(default_factory=lambda: set(map(Path, ("stubs", "cmake", "Win32", "x64"))))

    @staticmethod
    @override
    def path_feature_detector(path: Path) -> Set[CudaArch]:
        """
        Equivalent to the following bash snippet, sans ordering:

        ```console
        $ cuobjdump libcublas.so | grep 'arch =' | sort -u
        arch = sm_35
        ...
        arch = sm_86
        arch = sm_90
        ```
        """
        logging.debug(f"Running cuobjdmp on {path}...")
        start_time = time.time()
        result = subprocess.run(
            ["cuobjdump", path],
            capture_output=True,
            check=False,
        )
        end_time = time.time()
        logging.debug(f"Ran cuobjdump on {path} in {end_time - start_time} seconds.")

        # Handle failure and the case where the library is GPU-agnostic.
        if result.returncode != 0:
            err_msg = result.stderr.decode("utf-8")
            if "does not contain device code" in err_msg:
                logging.debug(f"{path} is GPU-agnostic.")
                return set()

            raise RuntimeError(f"Failed to run cuobjdump on {path}: {err_msg}")

        output = result.stdout.decode("utf-8")
        architecture_strs: set[str] = set(re.findall(r"^arch = (.+)$", output, re.MULTILINE))
        architectures: set[CudaArch] = set(map(CudaArchTA.validate_python, architecture_strs))
        logging.debug(f"Found architectures: {architectures}")
        return architectures

    @staticmethod
    @override
    def path_filter(path: Path) -> bool:
        return path.suffix == ".so"

    @override
    def find(self, store_path: Path) -> None | Sequence[CudaArch] | Mapping[str, Sequence[CudaArch]]:
        logging.debug(f"Getting supported CUDA architectures for {store_path}...")
        start_time = time.time()
        ret = super().find(store_path)
        end_time = time.time()
        logging.debug(f"Got supported CUDA architectures for {store_path} in {end_time - start_time} seconds: {ret}")
        return ret
