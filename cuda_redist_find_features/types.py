from __future__ import annotations

from collections.abc import Callable, ItemsView, Iterable, KeysView, Mapping, Sequence, ValuesView
from concurrent.futures import Executor, Future
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import Annotated, Any, Generic, Literal, Self, TypeVar, cast, final, get_args, overload

import pydantic
from pydantic import BaseModel, ConfigDict, DirectoryPath, Field, FilePath, HttpUrl, RootModel, TypeAdapter
from typing_extensions import TypeAliasType

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LogLevels = cast(Sequence[LogLevel], get_args(LogLevel))

model_config = ConfigDict(
    frozen=True,
    populate_by_name=True,
    revalidate_instances="always",
    strict=True,
    validate_assignment=True,
    validate_default=True,
)

validate_call = pydantic.validate_call(config=model_config)

TA: partial[TypeAdapter[Any]] = partial(TypeAdapter, config=model_config)
FF = partial(Field, frozen=True)
SFF = partial(Field, frozen=True, strict=True)

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class SFMRM(RootModel[Mapping[K, V]]):
    """
    Root model for a mapping.
    """

    model_config = model_config
    root: Mapping[K, V]

    @overload
    def get(self, __key: K) -> V | None:
        ...

    @overload
    def get(self, __key: K, __default: V) -> V:
        ...

    @overload
    def get(self, __key: K, __default: T) -> V | T:
        ...

    def get(self, key: K, default: T = None) -> V | T:
        "D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None."
        return self.root.get(key, default)

    def keys(self):
        "D.keys() -> a set-like object providing a view on D's keys"
        return KeysView(self.root)

    def items(self):
        "D.items() -> a set-like object providing a view on D's items"
        return ItemsView(self.root)

    def values(self):
        "D.values() -> an object providing a view on D's values"
        return ValuesView(self.root)

    @validate_call
    def __len__(self) -> int:
        return self.root.__len__()

    @validate_call
    def __contains__(self, key: K) -> bool:
        return self.root.__contains__(key)

    @validate_call
    def __getitem__(self, key: K) -> V:
        return self.root.__getitem__(key)


class SFBM(BaseModel):
    """
    Base model.
    """

    model_config = model_config


FilePathTA: TypeAdapter[FilePath] = TA(FilePath)
DirectoryPathTA: TypeAdapter[DirectoryPath] = TA(DirectoryPath)
HttpUrlTA: TypeAdapter[HttpUrl] = TA(HttpUrl)

_Platform = Literal[
    "linux-aarch64",
    "linux-ppc64le",
    "linux-sbsa",
    "linux-x86_64",
    "windows-x86_64",
]
Platform = TypeAliasType(
    "Platform",
    Annotated[
        _Platform,
        # NOTE: Cannot use strict with literals/unions.
        FF(description="A platform name."),
    ],
)
Platforms = cast(Iterable[Platform], get_args(_Platform))
PlatformTA: TypeAdapter[Platform] = TA(Platform)

PackageName = TypeAliasType(
    "PackageName",
    Annotated[
        str,
        SFF(
            description="The name of a package.",
            examples=["cuda_cccl", "cuda_nvcc"],
        ),
    ],
)
PackageNameTA: TypeAdapter[PackageName] = TA(PackageName)

CudaArch = TypeAliasType(
    "CudaArch",
    Annotated[
        str,
        SFF(
            description="A CUDA architecture name.",
            examples=["sm_35", "sm_50", "sm_60", "sm_70", "sm_75", "sm_80", "sm_86", "sm_90a"],
            pattern=r"^sm_\d+[a-z]?$",
        ),
    ],
)
CudaArchTA: TypeAdapter[CudaArch] = TA(CudaArch)

LibSoName = TypeAliasType(
    "LibSoName",
    Annotated[
        str,
        SFF(
            description="The name of a shared object file.",
            examples=["libcuda.so", "libcuda.so.1", "libcuda.so.1.2.3"],
            pattern=r"\.so(?:\.\d+)*$",
        ),
    ],
)
LibSoNameTA: TypeAdapter[LibSoName] = TA(LibSoName)


Md5 = TypeAliasType(
    "Md5",
    Annotated[
        str,
        SFF(
            description="An MD5 hash.",
            examples=["0123456789abcdef0123456789abcdef"],
            pattern=r"[0-9a-f]{32}",
        ),
    ],
)

Sha256 = TypeAliasType(
    "Sha256",
    Annotated[
        str,
        SFF(
            description="A SHA256 hash.",
            examples=["0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"],
            pattern=r"[0-9a-f]{64}",
        ),
    ],
)


@final
class FutureStatus(Enum):
    WAITING = ":zzz:"
    RUNNING = ":clock5:"
    DONE = ":white_check_mark:"
    CANCELLED = ":x:"

    @classmethod
    def of(cls, future: Future[Any]) -> Self:
        if future.cancelled():
            return cls.CANCELLED
        elif future.done():
            return cls.DONE
        elif future.running():
            return cls.RUNNING
        else:
            return cls.WAITING


A = TypeVar("A")
B = TypeVar("B")


@final
@dataclass(frozen=True, order=True, slots=True)
class Task(Generic[A, B]):
    initial: A
    status: FutureStatus
    future: Future[B]

    def update_status(self) -> Self:
        return __class__(
            initial=self.initial,
            status=FutureStatus.of(self.future),
            future=self.future,
        )

    def is_complete(self) -> bool:
        return self.status in {FutureStatus.DONE, FutureStatus.CANCELLED}

    def is_waiting(self) -> bool:
        return self.status == FutureStatus.WAITING

    def is_running(self) -> bool:
        return self.status == FutureStatus.RUNNING

    @classmethod
    def submit(cls, executor: Executor, initial: A, fn: Callable[[A], B]) -> Task[A, B]:
        return cls(
            initial=initial,
            status=FutureStatus.WAITING,
            future=executor.submit(fn, initial),
        )
