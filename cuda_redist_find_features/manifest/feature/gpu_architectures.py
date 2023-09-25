import logging
import subprocess
import time
from itertools import chain
from pathlib import Path
from typing import Mapping, Sequence

from pydantic import BaseModel
from typing_extensions import Self

from cuda_redist_find_features.types import GPU_ARCHITECTURE_PATTERN, GpuArchitecture


def cuobjdump_for_architectures(lib_path: Path) -> set[GpuArchitecture]:
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


class FeatureGpuArchitectures(BaseModel):
    """
    Maps libraries to the GPU architectures they support.
    """

    __root__: Mapping[str, Sequence[GpuArchitecture]]

    @classmethod
    def of(cls, store_path: Path) -> Self:
        logging.debug(f"Getting gencodes for {store_path}...")
        start_time = time.time()
        lib = store_path / "lib"

        libs: dict[Path, set[GpuArchitecture]] = {
            lib_path: cuobjdump_for_architectures(lib_path) for lib_path in chain(lib.rglob("*.so"), lib.rglob("*.a"))
        }

        # A library may have either:
        # - No architectures, in which case it is GPU-agnostic.
        # - One or more architectures, in which case it is GPU-specific.
        # If a library has one or more architectures, it must have the same architectures as all other libraries.
        device_specific_libraries: dict[Path, set[GpuArchitecture]] = {
            lib_path: archs for lib_path, archs in libs.items() if len(archs) > 0
        }

        # The device specific libraries should all have the same set of architectures.
        # Note: in the case of packages supporting multiple versions of CUDA, there will be multiple directories under
        # lib. The test only fails libraries within a single directory for supporting different architectures.
        # TODO: Quadratic, but whatever.
        for path1, archs1 in device_specific_libraries.items():
            for path2, archs2 in device_specific_libraries.items():
                # Skip if they are not in the same directory.
                if path1.parent != path2.parent:
                    logging.debug(f"Skipping comparison of {path1} and {path2} because they are not in the same dir.")
                    continue

                # Skip if they support the same architectures.
                if archs1 == archs2:
                    continue

                # Otherwise, raise a warning.
                logging.warning(
                    f"Expected {path1} to support the same architectures as sibling {path2}: expected"
                    f" {sorted(archs2)} but got {sorted(archs1)}."
                )

        end_time = time.time()
        logging.debug(f"Got gencodes for {store_path} in {end_time - start_time} seconds.")

        libs_serializable: dict[str, list[GpuArchitecture]] = {
            path.relative_to(store_path).as_posix(): sorted(archs) for path, archs in libs.items()
        }

        return cls.parse_obj(libs_serializable)
