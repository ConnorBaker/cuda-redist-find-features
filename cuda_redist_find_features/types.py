import re
from pathlib import Path
from typing import Literal, NewType, TypeAlias

from pydantic import HttpUrl

Architecture: TypeAlias = Literal[
    "linux-aarch64",
    "linux-ppc64le",
    "linux-sbsa",
    "linux-x86_64",
    "windows-x86_64",
]

GpuArchitecture = NewType("GpuArchitecture", str)

GPU_ARCHITECTURE_PATTERN = re.compile(r"arch = (sm_\d+)")

LibSoName = NewType("LibSoName", str)

Md5 = NewType("Md5", str)

Ref: TypeAlias = HttpUrl | Path

Sha256 = NewType("Sha256", str)
