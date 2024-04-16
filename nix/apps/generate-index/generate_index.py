# TO USE:
# Run `nix run .#generate-index` from the root of the repo.
import concurrent.futures
import dataclasses
import json
import re
import subprocess
from collections import defaultdict
from collections.abc import Container, Iterable, Sequence
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Final,
    Literal,
    Self,
    cast,
    final,
    get_args,
)
from urllib import request

IndexPath: Final[str] = "./nix/apps/generate-index/index.json"
type IgnoredPlatform = Literal["windows-x86_64"]
IgnoredPlatforms: Container[IgnoredPlatform] = set(get_args(IgnoredPlatform.__value__))
type Platform = Literal[
    "linux-aarch64",
    "linux-ppc64le",
    "linux-sbsa",
    "linux-x86_64",
]
Platforms: Container[Platform] = set(get_args(Platform.__value__))
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
RedistNames: Container[RedistName] = set(get_args(RedistName.__value__))
RedistUrlPrefix: Final[str] = "https://developer.download.nvidia.com/compute"

if TYPE_CHECKING:
    from _typeshed import DataclassInstance
else:
    DataclassInstance = object


class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, o: object):
        try:
            return dataclasses.asdict(o)  # type: ignore
        except TypeError:
            return super().default(o)


def generic_dataclass_populate[I: DataclassInstance](
    cls: type[I],
    d: dict[str, Any],
    *,
    key_prefix: str = "",
    check_empty: bool = True,
    discard_fields: Iterable[str] = [],
    **external_fields: Any,
) -> tuple[I, dict[str, Any]]:
    """
    Creates an instance of a dataclass from the provided dictionary, removing the fields
    used to create the instance from the dictionary.

    Args:
    - cls: The dataclass type to create an instance of.
    - d: The dictionary to create the instance from.
    - key_prefix: The prefix to use for the keys in the dictionary.
    - check_empty: Whether to check if the dictionary is empty after creating the instance.
    - external_fields: Additional fields to provide to the dataclass constructor.
    """
    kwargs: dict[str, Any] = {}

    # Remove fields to discard.
    for field_name in discard_fields:
        if field_name in d:
            del d[field_name]

    for field in dataclasses.fields(cls):
        key = field.name

        # No need to check the type of the argument provided by the caller.
        if key in external_fields:
            value = external_fields[key]
        else:
            value = d.pop(key_prefix + key, None)
            if not isinstance(value, field.type):
                raise TypeError(
                    f"Expected {field.type} for {key} in {cls.__name__}, got {type(value)} while processing {d}"
                )

        kwargs[key] = value

    if check_empty and d != {}:
        raise RuntimeError(f"Expected dictionary to be empty after populating {cls}, got {d}")

    return cls(**kwargs), d


@final
@dataclasses.dataclass(order=True, kw_only=True, slots=True)
class ManifestInfo:
    """
    Top-level keys in the manifest prefixed with release_, augmented with the redist_name.
    """

    date: None | str = None
    label: None | str = None
    product: None | str = None
    redist_name: RedistName = dataclasses.field()

    @classmethod
    def mk(cls: type[Self], redist_name: RedistName, manifest: dict[str, Any]) -> tuple[Self, dict[str, Any]]:
        """
        Creates an instance of ManifestInfo from the provided manifest dictionary, removing the fields
        used to create the instance from the dictionary.
        """
        return generic_dataclass_populate(
            cls,
            manifest,
            key_prefix="release_",
            check_empty=False,
            redist_name=redist_name,
        )


@final
@dataclasses.dataclass(order=True, kw_only=True, slots=True)
class ReleaseInfo:
    """
    Top-level values in the manifest from keys not prefixed with release_, augmented with the package_name.
    """

    license_path: None | str = None
    license: None | str = None
    name: None | str = None
    package_name: str = dataclasses.field()
    version: str = dataclasses.field()

    @classmethod
    def mk(cls: type[Self], package_name: str, release: dict[str, Any]) -> tuple[Self, dict[str, Any]]:
        """
        Creates an instance of ReleaseInfo from the provided manifest dictionary, removing the fields
        used to create the instance from the dictionary.
        """
        return generic_dataclass_populate(
            cls,
            release,
            discard_fields=["cuda_variant"],
            check_empty=False,
            package_name=package_name,
        )


@final
@dataclasses.dataclass(order=True, kw_only=True, slots=True)
class PackageInfo:
    cuda_variant: None | str = None
    platform: Platform = dataclasses.field()
    relative_path: str = dataclasses.field()
    hash: str = dataclasses.field()

    @classmethod
    def mk(cls: type[Self], platform: Platform, package: dict[str, Any]) -> Iterable[Self]:
        """
        Creates an instance of PackageInfo from the provided manifest dictionary, removing the fields
        used to create the instance from the dictionary.
        NOTE: Because the keys may be prefixed with "cuda", indicating multiple packages, we return a sequence of
        PackageInfo instances.
        """
        # Two cases: either our keys are package keys, or they're boxed inside an object mapping a prefixed CUDA version
        # (e.g., "cuda11") to the package keys.
        all_cuda_keys: bool = all(key.startswith("cuda") for key in package.keys())
        any_cuda_keys: bool = any(key.startswith("cuda") for key in package.keys())

        if any_cuda_keys and not all_cuda_keys:
            raise RuntimeError(
                f"Expected all package keys to start with 'cuda' or none to start with 'cuda', got {package.keys()}"
            )

        packages: dict[None | str, Any] = {None: package} if not any_cuda_keys else package  # type: ignore
        infos: list[Self] = []
        for cuda_variant_name in set(packages.keys()):
            package = packages.pop(cuda_variant_name)
            sha256 = package.pop("sha256")
            info, _ = generic_dataclass_populate(
                cls,
                package,
                check_empty=True,
                discard_fields=["size", "md5"],
                cuda_variant=cuda_variant_name.removeprefix("cuda") if cuda_variant_name is not None else None,
                hash=sha256,
                platform=platform,
            )
            infos.append(info)

        infos.sort()
        return infos


@final
@dataclasses.dataclass(order=True, slots=True)
class RestructuredRelease:
    release_info: ReleaseInfo
    packages: Sequence[PackageInfo]

    @classmethod
    def mk(cls: type[Self], package_name: str, release: dict[str, Any]) -> Self:
        release_info, release = ReleaseInfo.mk(package_name, release)

        # Remove ignored platforms if they exist.
        for ignored_platform in IgnoredPlatforms:
            if ignored_platform in release:
                del release[ignored_platform]

        # Check if the source field exists -- it's an object with keys equivalent to what PackageInfo needs.
        # If it does exist (it is exclusive with platform keys), we need to nest the source object under the platform
        # keys.
        source_key_exists: bool = "source" in release
        platform_keys_exist: bool = any(platform in release for platform in Platforms)
        if source_key_exists and platform_keys_exist:
            raise RuntimeError(f"Expected source and platform keys to be exclusive, got {release.keys()}")

        # If the source key exists, we need to nest the source object under the platform keys.
        if source_key_exists:
            source = release.pop("source")
            if not isinstance(source, dict):
                raise RuntimeError(f"Expected source to be an object, got {type(source)}")
            for platform in Platforms:
                # Must copy the source object to avoid modifying the original later.
                release[platform] = source.copy()

        # Check that the keys are valid.
        key_set = set(release.keys())
        if (key_set - Platforms) != set():
            raise RuntimeError(f"Expected keys to be in {Platforms}, got {key_set}")

        packages: list[PackageInfo] = [
            package_info
            for platform in key_set
            for package_info in PackageInfo.mk(cast(Platform, platform), release.pop(platform))
        ]
        packages.sort()

        if release != {}:
            raise RuntimeError(f"Expected release for {release_info} to be empty after processing, got {release}")
        return cls(release_info, packages)


@final
@dataclasses.dataclass(order=True, slots=True)
class RestructuredManifest:
    manifest_info: ManifestInfo
    releases: Sequence[RestructuredRelease]

    @classmethod
    def mk(cls, redist_name: RedistName, manifest_or_version: str | dict[str, Any]) -> Self:
        match manifest_or_version:
            case str() as version:
                return cls._mk_from_version(redist_name, version)
            case dict() as manifest:
                return cls._mk_from_manifest(redist_name, manifest)

    @classmethod
    def _mk_from_manifest(cls, redist_name: RedistName, manifest: dict[str, Any]) -> Self:
        manifest_info, manifest = ManifestInfo.mk(redist_name, manifest)

        releases: list[RestructuredRelease] = [
            release
            for package_name in set(manifest.keys())
            # Don't include releases for packages that have no packages for the platforms we care about.
            if (release := RestructuredRelease.mk(package_name, manifest.pop(package_name))).packages != []
        ]
        releases.sort()

        if manifest != {}:
            raise RuntimeError(f"Expected manifest for {manifest_info} to be empty after processing, got {manifest}")
        return cls(manifest_info, releases)

    @classmethod
    def _mk_from_version(cls, redist_name: RedistName, version: str) -> Self:
        return cls.mk(redist_name, get_manifest(redist_name, version))


@final
@dataclasses.dataclass(order=True, slots=True)
class NixStoreEntry:
    hash: str
    store_path: Path

    @classmethod
    def from_url(cls, url: str, sha256: str) -> Self:
        """
        Adds a release to the Nix store.

        NOTE: By specifying the hash type and expected hash, we avoid redownloading.
        """
        result = subprocess.run(
            [
                "nix",
                "store",
                "prefetch-file",
                "--json",
                "--hash-type",
                "sha256",
                "--expected-hash",
                sha256,
                url,
            ],
            capture_output=True,
            check=True,
        )
        return cls(**json.loads(result.stdout))

    @classmethod
    def unpack_archive(cls, store_path: Path) -> Self:
        """
        Uses nix flake prefetch to unpack an archive and return the recursive NAR hash.

        NOTE: Only operate in the Nix store to avoid redownloading the archive.
        NOTE: This command is smart enough to not re-unpack archives when in the nix store, unlike
        nix store prefetch-file.
        """
        result = subprocess.run(
            ["nix", "flake", "prefetch", "--json", store_path.as_uri()],
            capture_output=True,
            check=True,
        )
        return cls(**json.loads(result.stdout))

    @classmethod
    def get_nar_hash_from_url(cls, url: str, sha256: str) -> str:
        """
        Composes from_url and unpack_archive to get the NAR hash from a URL.
        """
        tarball = cls.from_url(url, sha256)
        return cls.unpack_archive(tarball.store_path).hash


def get_manifest_versions(redist_name: RedistName) -> Sequence[str]:
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
        return [matched.group(2) for matched in re.finditer(regex_str, s, flags=re.VERBOSE)]


def get_manifest(redist_name: RedistName, version: str) -> dict[str, Any]:
    with request.urlopen(f"{RedistUrlPrefix}/{redist_name}/redist/redistrib_{version}.json") as response:
        content_bytes = response.read()
        maybe_obj = json.loads(content_bytes)
        if not isinstance(maybe_obj, dict):
            raise RuntimeError(f"Expected JSON object for manifest {redist_name} {version}, got {type(maybe_obj)}")
        return maybe_obj  # type: ignore


if __name__ == "__main__":
    # Redist name to versions to restricted manifest
    index: dict[str, dict[str, RestructuredManifest]] = defaultdict(dict)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Get all of the manifests in parallel.
        futures = {
            executor.submit(RestructuredManifest.mk, redist_name, version): (redist_name, version)
            for redist_name in RedistNames
            for version in get_manifest_versions(redist_name)
        }
        num_tasks = len(futures)
        print(f"Downloading and processing {num_tasks} manifests...")
        for tasks_completed, future in enumerate(concurrent.futures.as_completed(futures)):
            (redist_name, version) = futures[future]
            try:
                data = future.result()
                index[redist_name][version] = data
                print(f"({tasks_completed + 1}/{num_tasks}): Processed manifest for {redist_name} {version}")
            except TypeError:
                # This error largely happens when processing earlier versions of the CUDA manifest (pre-11.5) because it
                # doesn't follow the same structure as the later versions.
                print(
                    f"({tasks_completed + 1}/{num_tasks}): "
                    + f"Skipped manifest for {redist_name} {version} due to type error"
                )
            except Exception as e:
                raise RuntimeError(f"Error processing manifest for {redist_name} version {version}: {e}")

        # Ensure all of the tarballs are in the store.
        futures = {
            executor.submit(
                NixStoreEntry.get_nar_hash_from_url,
                f"{RedistUrlPrefix}/{redist_name}/redist/{package.relative_path}",
                package.hash,
            ): (
                redist_name,
                version,
                release_idx,
                package_idx,
            )
            for redist_name, versions in index.items()
            for version, manifest in versions.items()
            for release_idx, release in enumerate(manifest.releases)
            for package_idx, package in enumerate(release.packages)
        }
        num_tasks = len(futures)
        print(f"Downloading, unpacking, and finding the narHash of {num_tasks} tarballs...")
        for tasks_completed, future in enumerate(concurrent.futures.as_completed(futures)):
            (
                redist_name,
                version,
                release_idx,
                package_idx,
            ) = futures[future]
            package = index[redist_name][version].releases[release_idx].packages[package_idx]
            try:
                nar_hash = future.result()
                package.hash = nar_hash
                print(f"({tasks_completed + 1}/{num_tasks}): Processed narHash for {package.relative_path}")
            except Exception as e:
                raise RuntimeError(f"Error downloading or unpacking {package.relative_path}: {e}")

    with open(IndexPath, "w", encoding="utf-8") as file:
        json.dump(
            index,
            file,
            indent=2,
            sort_keys=True,
            cls=DataclassJSONEncoder,
        )
