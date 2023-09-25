import logging
import subprocess
import time
from functools import reduce
from itertools import chain
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from pydantic import BaseModel
from typing_extensions import Self

from cuda_redist_find_features.types import GPU_ARCHITECTURE_PATTERN, GpuArchitecture


def cuobjdump_lib_path(lib_path: Path) -> set[GpuArchitecture]:
    """
    Equivalent to the following bash snippet:

    ```console
    $ cuobjdump libcublas.so | grep 'arch =' | sort -u
    arch = sm_35
    ...
    arch = sm_86
    arch = sm_90
    ```
    """
    logging.debug(f"Running cuobjdmp on {lib_path}...")
    start_time = time.time()
    result = subprocess.run(
        ["cuobjdump", lib_path],
        capture_output=True,
        check=False,
    )
    end_time = time.time()
    logging.debug(f"Ran cuobjdump on {lib_path} in {end_time - start_time} seconds.")

    # Handle failure and the case where the library is GPU-agnostic.
    if result.returncode != 0:
        err_msg = result.stderr.decode("utf-8")
        if "does not contain device code" in err_msg:
            logging.debug(f"{lib_path} is GPU-agnostic.")
            return set()

        raise RuntimeError(f"Failed to run cuobjdump on {lib_path}: {err_msg}")

    output = result.stdout.decode("utf-8")
    architectures: set[GpuArchitecture] = set(GPU_ARCHITECTURE_PATTERN.findall(output))
    logging.debug(f"Found architectures: {architectures}")
    return architectures


def cuobjdump_lib_paths(lib_paths: Iterable[Path]) -> list[GpuArchitecture]:
    return sorted(reduce(set.union, map(cuobjdump_lib_path, lib_paths), set()))


class FeatureGpuArchitectures(BaseModel):
    """
    Maps libraries to the GPU architectures they support.
    """

    __root__: Sequence[GpuArchitecture] | Mapping[str, Sequence[GpuArchitecture]]

    @classmethod
    def of(cls, store_path: Path) -> Self:
        lib = store_path / "lib"

        if not lib.exists():
            logging.debug(f"{lib} does not exist, no gencodes to find")
            return cls.parse_obj([])

        logging.debug(f"Getting gencodes for {store_path}...")
        start_time = time.time()

        # Stub directory does not have any libraries.
        # Ignore the cmake directory which is used for distribution builds.
        # Windows directories
        ignored_dirs: set[str] = {"stubs", "cmake", "Win32", "x64"}

        # Two mutually-exclusive cases:
        #
        # 1. There are subdirectories other than stubs present under lib.
        # 2. There are libraries present directly under lib.
        #
        # In case 1, we should not have any libraries directly under lib.
        # In case 2, we should not have any subdirectories other than stubs present under lib.
        lib_subdirs: list[Path] = []
        lib_library_paths: list[Path] = []
        for item in lib.iterdir():
            if item.is_dir():
                if item.name not in ignored_dirs:
                    logging.debug(f"Found subdirectory {item.name} under {lib}.")
                    lib_subdirs.append(item)
                else:
                    logging.debug(f"Ignoring {item.name} because it is an ignored directory ({ignored_dirs}).")
            elif item.is_file() and item.suffix in {".so", ".a"}:
                logging.debug(f"Found library {item.name} under {lib}.")
                lib_library_paths.append(item)

        if len(lib_subdirs) > 0 and len(lib_library_paths) > 0:
            raise RuntimeError(
                f"Found both subdirectories and libraries directly under {lib}."
                f" Subdirectories: {lib_subdirs}."
                f" Libraries: {lib_library_paths}."
            )

        ret: list[GpuArchitecture] | dict[str, list[GpuArchitecture]]
        if len(lib_subdirs) > 0:
            # Take the union of all the capabilities of the libraries in the subdirectory.
            ret = {
                lib_subdir.relative_to(store_path).as_posix(): cuobjdump_lib_paths(
                    chain(lib_subdir.glob("*.so"), lib_subdir.glob("*.a"))
                )
                for lib_subdir in lib_subdirs
            }
        elif len(lib_library_paths) > 0:
            ret = cuobjdump_lib_paths(lib_library_paths)
        else:
            ret = []

        end_time = time.time()
        logging.debug(f"Got gencodes for {store_path} in {end_time - start_time} seconds.")

        return cls.parse_obj(ret)
