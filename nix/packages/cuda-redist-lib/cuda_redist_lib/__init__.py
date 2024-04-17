# NOTE: Open bugs in Pydantic like https://github.com/pydantic/pydantic/issues/8984 prevent the full switch to the type
# keyword introduced in Python 3.12.
import base64
import concurrent.futures
import json
import operator
import re
from collections import defaultdict
from collections.abc import Container, ItemsView, Iterator, KeysView, Mapping, Sequence, ValuesView
from functools import partial
from pathlib import Path
from typing import (
    Annotated,
    Any,
    Final,
    Literal,
    Self,
    TypeAlias,
    cast,
    get_args,
    overload,
)
from urllib import request

from pydantic import BaseModel, ConfigDict, DirectoryPath, Field, FilePath, HttpUrl, RootModel, TypeAdapter
from pydantic.alias_generators import to_camel

ModelConfig: Final[ConfigDict] = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
    revalidate_instances="always",
    strict=True,
    validate_assignment=True,
    validate_default=True,
)

# NOTE: pydantic.errors.PydanticUserError: Cannot use `config` when the type is a BaseModel, dataclass or TypedDict.
# These types can have their own config and setting the config via the `config` parameter to TypeAdapter will not
# override it, thus the `config` you passed to TypeAdapter becomes meaningless, which is probably not what you want.
PydanticTypeAdapter: Final[partial[TypeAdapter[Any]]] = partial(TypeAdapter, config=ModelConfig)

FilePathTA: Final[TypeAdapter[FilePath]] = PydanticTypeAdapter(FilePath)
DirectoryPathTA: Final[TypeAdapter[DirectoryPath]] = PydanticTypeAdapter(DirectoryPath)
HttpUrlTA: Final[TypeAdapter[HttpUrl]] = PydanticTypeAdapter(HttpUrl)


class PydanticSequence[T](RootModel[Sequence[T]]):
    """
    Root model for a sequence.
    """

    model_config = ModelConfig

    root: Sequence[T]

    def __len__(self) -> int:
        return self.root.__len__()

    def __getitem__(self, index: int) -> T:
        return self.root.__getitem__(index)

    def __iter__(self) -> Iterator[T]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self.root.__iter__()

    def __contains__(self, item: T) -> bool:
        return self.root.__contains__(item)


class PydanticMapping[K, V](RootModel[Mapping[K, V]]):
    """
    Root model for a mapping.
    """

    model_config = ModelConfig

    root: Mapping[K, V]

    @overload
    def get(self, __key: K) -> V | None: ...

    @overload
    def get(self, __key: K, __default: V) -> V: ...

    @overload
    def get[T](self, __key: K, __default: T) -> V | T: ...

    def get[T](self, key: K, default: T = None) -> V | T:
        "D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None."
        return self.root.get(key, default)

    def keys(self) -> KeysView[K]:
        "D.keys() -> a set-like object providing a view on D's keys"
        return KeysView(self.root)

    def items(self) -> ItemsView[K, V]:
        "D.items() -> a set-like object providing a view on D's items"
        return ItemsView(self.root)

    def values(self) -> ValuesView[V]:
        "D.values() -> an object providing a view on D's values"
        return ValuesView(self.root)

    def __len__(self) -> int:
        return self.root.__len__()

    def __contains__(self, key: K) -> bool:
        return self.root.__contains__(key)

    def __getitem__(self, key: K) -> V:
        return self.root.__getitem__(key)


class PydanticObject(BaseModel):
    """
    Base model.
    """

    model_config = ModelConfig


type IgnoredPlatform = Literal["windows-x86_64"]
IgnoredPlatforms: Final[Container[IgnoredPlatform]] = set(get_args(IgnoredPlatform.__value__))

type Platform = Literal[
    "source",  # Source-agnostic
    "linux-aarch64",
    "linux-ppc64le",
    "linux-sbsa",
    "linux-x86_64",
]
Platforms: Final[Container[Platform]] = set(get_args(Platform.__value__))

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
RedistNames: Final[Container[RedistName]] = set(get_args(RedistName.__value__))

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


def sha256_to_sri_hash(sha256: Sha256) -> SriHash:
    """
    Convert a Base16 SHA-256 hash to a Subresource Integrity (SRI) hash.
    """
    sha256_bytes = bytes.fromhex(sha256)
    base64_hash = base64.b64encode(sha256_bytes).decode("utf-8")
    sri_hash = f"sha256-{base64_hash}"
    return SriHashTA.validate_strings(sri_hash)


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

PackageVariants: TypeAlias = PydanticMapping[None | CudaVariant, SriHash]

Packages: TypeAlias = PydanticMapping[Platform, PackageVariants]


# Returns true if the version should be ignored.
def is_ignored_nvidia_manifest(redist_name: RedistName, version: Version) -> bool:
    match redist_name:
        # These CUDA manifests are old enough that they don't conform to the same structure as the newer ones.
        case "cuda":
            return version in {
                "11.0.3",
                "11.1.1",
                "11.2.0",
                "11.2.1",
                "11.2.2",
                "11.3.0",
                "11.3.1",
                "11.4.0",
                "11.4.1",
            }
        # The cuDNN manifests with four-component versions don't have a cuda_variant field.
        # The three-component versions are fine.
        case "cudnn":
            return len(version.split(".")) == 4  # noqa: PLR2004
        case _:
            return False


class ReleaseInfo(PydanticObject):
    """
    Top-level values in the manifest from keys not prefixed with release_, augmented with the package_name.
    """

    license_path: None | Path = None
    license: None | str = None
    name: None | str = None
    version: Version

    @classmethod
    def mk(cls: type[Self], nvidia_release: dict[str, Any]) -> Self:
        """
        Creates an instance of ReleaseInfo from the provided manifest dictionary, removing the fields
        used to create the instance from the dictionary.
        """
        kwargs = {name: nvidia_release.pop(name, None) for name in ["license_path", "license", "name", "version"]}
        kwargs["license_path"] = Path(kwargs["license_path"]) if kwargs["license_path"] is not None else None
        return cls.model_validate(kwargs)


def mk_package_hashes(
    package_name: PackageName,
    release_info: ReleaseInfo,
    platform: Platform,
    nvidia_package: dict[str, Any],
) -> PackageVariants:
    """
    Creates an instance of PackageInfo from the provided manifest dictionary, removing the fields
    used to create the instance from the dictionary.
    NOTE: Because the keys may be prefixed with "cuda", indicating multiple packages, we return a sequence of
    PackageInfo instances.
    """
    # Two cases: either our keys are package keys, or they're boxed inside an object mapping a prefixed CUDA version
    # (e.g., "cuda11") to the package keys.
    all_cuda_keys: bool = all(key.startswith("cuda") for key in nvidia_package.keys())
    any_cuda_keys: bool = any(key.startswith("cuda") for key in nvidia_package.keys())

    if any_cuda_keys and not all_cuda_keys:
        raise RuntimeError(
            f"Expected all package keys to start with 'cuda' or none to start with 'cuda', got {nvidia_package.keys()}"
        )

    packages: dict[None | str, Any] = {None: nvidia_package} if not any_cuda_keys else nvidia_package  # type: ignore
    infos: dict[None | CudaVariant, SriHash] = {}
    for cuda_variant_name in set(packages.keys()):
        nvidia_package = packages.pop(cuda_variant_name)

        # Verify that we can compute the correct relative path before throwing it away.
        actual_relative_path = Path(nvidia_package.pop("relative_path"))
        expected_relative_path = mk_relative_path(package_name, platform, release_info.version, cuda_variant_name)
        if actual_relative_path != expected_relative_path:
            raise RuntimeError(f"Expected relative path to be {expected_relative_path}, got {actual_relative_path}")

        infos[cuda_variant_name] = sha256_to_sri_hash(nvidia_package.pop("sha256"))

    return PackageVariants.model_validate(infos)


class Release(PydanticObject):
    release_info: ReleaseInfo
    packages: Packages

    @classmethod
    def mk(
        cls: type[Self],
        package_name: PackageName,
        nvidia_release: dict[str, Any],
    ) -> Self:
        release_info = ReleaseInfo.mk(nvidia_release)

        # Remove ignored platforms if they exist.
        for ignored_platform in IgnoredPlatforms:
            if ignored_platform in nvidia_release:
                del nvidia_release[ignored_platform]

        # Remove cuda_variant keys if they exist.
        if "cuda_variant" in nvidia_release:
            del nvidia_release["cuda_variant"]

        # Check that the keys are valid.
        key_set = set(nvidia_release.keys())
        if (key_set - Platforms) != set():
            raise RuntimeError(f"Expected keys to be in {Platforms}, got {key_set}")
        else:
            key_set = cast(set[Platform], key_set)

        packages: dict[Platform, PackageVariants] = {
            platform: mk_package_hashes(
                package_name,
                release_info,
                platform,
                nvidia_release.pop(platform),
            )
            for platform in key_set
        }

        if nvidia_release != {}:
            raise RuntimeError(
                f"Expected release for {release_info} to be empty after processing, got {nvidia_release}"
            )

        return cls.model_validate({"release_info": release_info, "packages": packages})


Manifest: TypeAlias = PydanticMapping[PackageName, Release]


def mk_manifest(redist_name: RedistName, version: Version, nvidia_manifest: None | dict[str, Any] = None) -> Manifest:
    if nvidia_manifest is None:
        nvidia_manifest = get_nvidia_manifest(redist_name, version)

    for key in map(partial(operator.add, "release_"), ["date", "label", "product"]):
        if key in nvidia_manifest:
            del nvidia_manifest[key]

    releases: dict[str, Release] = {
        package_name: release
        for package_name in map(PackageNameTA.validate_strings, set(nvidia_manifest.keys()))
        # Don't include releases for packages that have no packages for the platforms we care about.
        if len((release := Release.mk(package_name, nvidia_manifest.pop(package_name))).packages) != 0
    }

    if nvidia_manifest != {}:
        raise RuntimeError(f"Expected manifest for {redist_name} to be empty after processing, got {nvidia_manifest}")

    return Manifest.model_validate(releases)


VersionedManifests: TypeAlias = PydanticMapping[Version, Manifest]

Index: TypeAlias = PydanticMapping[RedistName, VersionedManifests]


def mk_index() -> Index:
    index: dict[RedistName, dict[Version, Manifest]] = defaultdict(dict)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Get all of the manifests in parallel.
        futures = {
            executor.submit(mk_manifest, redist_name, version): (redist_name, version)
            for redist_name in RedistNames
            for version in get_nvidia_manifest_versions(redist_name)
            if not is_ignored_nvidia_manifest(redist_name, version)
        }
        num_tasks = len(futures)
        print(f"Downloading and processing {num_tasks} manifests...")
        for tasks_completed, future in enumerate(concurrent.futures.as_completed(futures)):
            (redist_name, version) = futures[future]
            try:
                data = future.result()
                index[redist_name][version] = data
                print(f"({tasks_completed + 1}/{num_tasks}): Processed manifest for {redist_name} {version}")
            except Exception as e:
                raise RuntimeError(f"Error processing manifest for {redist_name} version {version}: {e}")

    return Index.model_validate(index)


def get_nvidia_manifest_versions(redist_name: RedistName) -> Sequence[Version]:
    regex_str = r"""
        href=                # Match 'href='
        ('|")                # Capture a single or double quote
        redistrib_           # Match 'redistrib_'
        (\d+(?:\.\d+){1,3})  # Capture a version number with 2-4 components
        \.json               # Match '.json'
        \1                   # Match the same quote as the first capture group
    """

    with request.urlopen(f"{RedistUrlPrefix}/{redist_name}/redist/index.html") as response:
        s: str = response.read().decode("utf-8")
        return [VersionTA.validate_strings(matched.group(2)) for matched in re.finditer(regex_str, s, flags=re.VERBOSE)]


def get_nvidia_manifest(redist_name: RedistName, version: str) -> dict[str, Any]:
    with request.urlopen(f"{RedistUrlPrefix}/{redist_name}/redist/redistrib_{version}.json") as response:
        content_bytes = response.read()
        maybe_obj = json.loads(content_bytes)
        if not isinstance(maybe_obj, dict):
            raise RuntimeError(f"Expected JSON object for manifest {redist_name} {version}, got {type(maybe_obj)}")
        return maybe_obj  # type: ignore


def mk_relative_path(
    package_name: PackageName,
    platform: Platform,
    version: Version,
    cuda_variant: None | CudaVariant,
) -> Path:
    return (
        Path(package_name)
        / platform
        / "-".join([
            package_name,
            platform,
            (version + (f"_{cuda_variant}" if cuda_variant is not None else "")),
            "archive.tar.xz",
        ])
    )
