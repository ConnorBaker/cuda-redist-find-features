from collections.abc import Sequence
from typing import Literal, cast, get_args

from pydantic import HttpUrl

from cuda_redist_find_features._types import HttpUrlTA

RedistName = Literal[
    "cublasmp",
    "cuda",
    "cudnn",
    "cudss",
    "cuquantum",
    "cusolvermp",
    "cusparselt",
    "cutensor",
    # "nvidia-driver",  # NOTE: Some of the earlier manifests don't follow our schemes
    "nvjpeg2000",
    "nvpl",
    "nvtiff",
]
RedistNames = cast(Sequence[RedistName], get_args(RedistName))


def get_redist_url_prefix(redist_name: RedistName) -> HttpUrl:
    return HttpUrlTA.validate_strings(f"https://developer.download.nvidia.com/compute/{redist_name}/redist")
