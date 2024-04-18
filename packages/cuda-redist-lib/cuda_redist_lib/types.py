# NOTE: Open bugs in Pydantic like https://github.com/pydantic/pydantic/issues/8984 prevent the full switch to the type
# keyword introduced in Python 3.12.
from collections.abc import Set
from typing import (
    Annotated,
    Final,
    Literal,
    get_args,
)

from pydantic import Field, TypeAdapter

from cuda_redist_lib.pydantic import PydanticTypeAdapter

type IgnoredPlatform = Literal["windows-x86_64"]
IgnoredPlatforms: Final[Set[IgnoredPlatform]] = set(get_args(IgnoredPlatform.__value__))

type Platform = Literal[
    "source",  # Source-agnostic
    "linux-aarch64",
    "linux-ppc64le",
    "linux-sbsa",
    "linux-x86_64",
]
Platforms: Final[Set[Platform]] = set(get_args(Platform.__value__))

type RedistName = Literal[
    "cublasmp",
    "cuda",
    "cudnn",
    "cudss",
    "cuquantum",
    "cusolvermp",
    "cusparselt",
    "cutensor",
    # NOTE: Some of the earlier manifests don't follow our scheme.
    # "nvidia-driver"
    "nvjpeg2000",
    "nvpl",
    "nvtiff",
]
RedistNames: Final[Set[RedistName]] = set(get_args(RedistName.__value__))

RedistUrlPrefix: Final[str] = "https://developer.download.nvidia.com/compute"

type Sha256 = Annotated[
    str,
    Field(
        description="A SHA256 hash.",
        examples=["0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"],
        pattern=r"[0-9a-f]{64}",
    ),
]
Sha256TA: Final[TypeAdapter[Sha256]] = PydanticTypeAdapter(Sha256)

type SriHash = Annotated[
    str,
    Field(
        description="An SRI hash.",
        examples=["sha256-LxcXgwe1OCRfwDsEsNLIkeNsOcx3KuF5Sj+g2dY6WD0="],
        pattern=r"(?<algorithm>md5|sha1|sha256|sha512)-[A-Za-z0-9+/]+={0,2}",
    ),
]
SriHashTA: Final[TypeAdapter[SriHash]] = PydanticTypeAdapter(SriHash)

type CudaVariant = Annotated[
    str,
    Field(
        description="A CUDA variant (only including major versions).",
        examples=["cuda10", "cuda11", "cuda12"],
        pattern=r"cuda\d+",
    ),
]
CudaVariantTA: Final[TypeAdapter[CudaVariant]] = PydanticTypeAdapter(CudaVariant)

type PackageName = Annotated[
    str,
    Field(
        description="The name of a package.",
        examples=["cublasmp", "cuda", "cudnn", "cudss", "cuquantum", "cusolvermp", "cusparselt", "cutensor"],
        pattern=r"[_a-z]+",
    ),
]
PackageNameTA: Final[TypeAdapter[PackageName]] = PydanticTypeAdapter(PackageName)

type Version = Annotated[
    str,
    Field(
        description="A version number with two-to-four components.",
        examples=["11.0.3", "450.00.1", "22.01.03"],
        pattern=r"\d+(?:\.\d+){1,3}",
    ),
]
VersionTA: Final[TypeAdapter[Version]] = PydanticTypeAdapter(Version)

type LibSoName = Annotated[
    str,
    Field(
        description="The name of a shared object file.",
        examples=["libcuda.so", "libcuda.so.1", "libcuda.so.1.2.3"],
        pattern=r"\.so(?:\.\d+)*$",
    ),
]
LibSoNameTA: TypeAdapter[LibSoName] = PydanticTypeAdapter(LibSoName)

type CudaArch = Annotated[
    str,
    Field(
        description="A CUDA architecture name.",
        examples=["sm_35", "sm_50", "sm_60", "sm_70", "sm_75", "sm_80", "sm_86", "sm_90a"],
        pattern=r"^sm_\d+[a-z]?$",
    ),
]
CudaArchTA: TypeAdapter[CudaArch] = PydanticTypeAdapter(CudaArch)
