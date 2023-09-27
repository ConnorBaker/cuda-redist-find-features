import logging
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from typing_extensions import override

from cuda_redist_find_features.types import LibSoName

from .groupable_feature_detector import GroupableFeatureDetector


def patchelf_print_soname(lib_path: Path) -> LibSoName:
    """
    Returns the soname of the given library.

    The value is equivalent to the following bash snippet:

    ```console
    $ patchelf --print-soname ./libcusolver/lib/libcusolver.so
    libcusolver.so.11
    ```
    """
    logging.debug(f"Running patchelf --print-soname on {lib_path}...")
    start_time = time.time()
    result = subprocess.run(
        ["patchelf", "--print-soname", lib_path],
        capture_output=True,
        check=True,
    )
    end_time = time.time()
    logging.debug(f"Ran patchelf --print-soname on {lib_path} in {end_time - start_time} seconds.")
    lib_so_name: LibSoName = LibSoName(result.stdout.decode("utf-8").strip())
    logging.debug(f"Lib soname: {lib_so_name}")
    return lib_so_name


@dataclass
class NeededLibsDetector(GroupableFeatureDetector[LibSoName]):
    """
    Either:

    - List of libs needed by the given libraries.
    - Mapping from subdirectory name to list of libs needed by the libraries in that subdirectory.
    """

    dir: Path = Path("lib")
    ignored_dirs: set[Path] = field(default_factory=lambda: set(map(Path, ("stubs", "cmake", "Win32", "x64"))))

    @staticmethod
    @override
    def path_feature_detector(path: Path) -> set[LibSoName]:
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
            LibSoName(lib_so_name) for lib_so_name in result.stdout.decode("utf-8").splitlines()
        }
        logging.debug(f"Libs needed: {libs_needed}")
        return libs_needed

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
