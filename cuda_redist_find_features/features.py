import logging
import multiprocessing
from pathlib import Path
from typing import Iterator, Literal, Sequence, TypeAlias, get_args

from pydantic import BaseModel, Field

from cuda_redist_find_features import generic, manifest
from cuda_redist_find_features.utilities import (
    NixStoreEntry,
    file_paths_matching,
    is_nonempty,
    nix_store_prefetch_file,
    nix_store_unpack_archive,
)

Output: TypeAlias = Literal[
    "bin",
    "dev",
    "doc",
    "lib",
    "static",
    "sample",
]


class ReleaseFeatures(BaseModel):
    root_dirs: Sequence[str] = Field(alias="rootDirs")
    has_bin: bool = Field(False, alias="hasBin")
    has_dev: bool = Field(False, alias="hasDev")
    has_doc: bool = Field(False, alias="hasDoc")
    has_lib: bool = Field(False, alias="hasLib")
    has_static: bool = Field(False, alias="hasStatic")
    has_sample: bool = Field(False, alias="hasSample")

    # TODO(@connorbaker): Include the following attributes:
    # - architectures: architectures supported by the package. May be empty.
    # - has_device_code: true if the package contains device code / is not a host-only package.

    def get_outputs(self) -> list[Output]:
        return [output for output in get_args(Output) if getattr(self, f"has_{output}", False)]


Package: TypeAlias = generic.Package[ReleaseFeatures]


def get_dynamic_libraries(path: Path) -> Iterator[Path]:
    """
    Returns a list of dynamic libraries in the directory tree of the given path.
    """
    return file_paths_matching(path, {"*.so", "*.so.*", "*.dylib", "*.dll"})


def get_static_libraries(path: Path) -> Iterator[Path]:
    """
    Returns a list of static libraries in the directory tree of the given path.
    """
    return file_paths_matching(path, {"*.a", "*.lib"})


def get_executables(path: Path) -> Iterator[Path]:
    """
    Returns a list of executable files in the directory tree of the given path.
    """
    return (entry for entry in file_paths_matching(path, {"*"}) if entry.stat().st_mode & 0o111)


def get_cmake_modules(path: Path) -> Iterator[Path]:
    """
    Returns a list of cmake modules in the directory tree of the given path.
    """
    return file_paths_matching(path, {"*.cmake"})


def get_headers(path: Path) -> Iterator[Path]:
    """
    Returns a list of header files in the directory tree of the given path.
    """
    return file_paths_matching(path, {"*.h", "*.hh", "*.hpp", "*.hxx"})


def get_python_modules(path: Path) -> Iterator[Path]:
    """
    Returns a list of python modules in the directory tree of the given path.
    """
    return file_paths_matching(path, {"*.py"})


def has_dynamic_libraries(path: Path) -> bool:
    """
    Returns true if the path contains any dynamic libraries in its directory tree.
    """
    return is_nonempty(get_dynamic_libraries(path))


def has_static_libraries(path: Path) -> bool:
    """
    Returns true if the path contains any static libraries in its directory tree.
    """
    return is_nonempty(get_static_libraries(path))


def has_executables(path: Path) -> bool:
    """
    Returns true if the path contains any executable files in its directory tree.
    """
    return is_nonempty(get_executables(path))


# TODO(@connorbaker): Implement a check for pkg-config files.
def has_cmake_modules(path: Path) -> bool:
    """
    Returns true if the path contains any cmake modules in its directory tree.
    """
    return is_nonempty(get_cmake_modules(path))


def has_headers(path: Path) -> bool:
    """
    Returns true if the path contains any header files in its directory tree.
    """
    return is_nonempty(get_headers(path))


def has_python_modules(path: Path) -> bool:
    """
    Returns true if the path contains any python modules in its directory tree.
    """
    return is_nonempty(get_python_modules(path))


def get_release_features(store_path: Path) -> ReleaseFeatures:
    # Roots must be hashable, so we cannot just use a set.
    root_dirs = {entry for entry in store_path.iterdir() if entry.is_dir()}
    features = ReleaseFeatures.parse_obj(
        {
            "rootDirs": sorted(root_dir.name for root_dir in root_dirs),
        }
    )
    logging.debug(f"Found roots: {features.root_dirs}")

    # A number of these checks are taken from https://github.com/NixOS/nixpkgs/blob/d4d822f526f1f72a450da88bf35abe132181170f/pkgs/build-support/setup-hooks/multiple-outputs.sh.

    # Check for bin output.
    # - bin
    features.has_bin |= (store_path / "bin").exists()

    # Check for dev output.
    # - include
    # - lib/pkgconfig
    # - share/pkgconfig
    # - lib/cmake
    # - share/aclocal
    features.has_dev |= any(
        dir.exists()
        for dir in (
            store_path / "include",
            store_path / "lib" / "pkgconfig",
            store_path / "share" / "pkgconfig",
            store_path / "lib" / "cmake",
            store_path / "share" / "aclocal",
        )
    )

    # Check for doc output.
    # - share/info
    # - share/doc
    # - share/gtk-doc
    # - share/devhelp/books
    # - share/man
    features.has_doc |= any(
        dir.exists()
        for dir in (
            store_path / "share" / "info",
            store_path / "share" / "doc",
            store_path / "share" / "gtk-doc",
            store_path / "share" / "devhelp" / "books",
            store_path / "share" / "man",
        )
    )

    # Check for lib output.
    # - lib
    if (_lib_dir := store_path / "lib").exists():
        logging.debug("Found lib directory, checking for libraries.")
        features.has_lib |= has_dynamic_libraries(_lib_dir)
        features.has_static |= has_static_libraries(_lib_dir)

    # Check for sample output.
    # - samples
    features.has_sample |= (store_path / "samples").exists()

    _headers = list(get_headers(store_path))
    logging.debug(f"Found {len(_headers)} headers.")
    _header_dirs = {path.parent.relative_to(store_path) for path in _headers}
    logging.debug(f"Found {len(_header_dirs)} header directories: {_header_dirs}")

    if len(_header_dirs) > 0 and not any(header_dir.is_relative_to("include") for header_dir in _header_dirs):
        logging.warning(f"Found directories containing headers outside include: {_header_dirs}.")

    _shared_libs = list(get_dynamic_libraries(store_path))
    logging.debug(f"Found {len(_shared_libs)} shared libraries.")
    _shared_lib_dirs = {path.parent.relative_to(store_path) for path in _shared_libs}
    logging.debug(f"Found {len(_shared_lib_dirs)} shared library directories: {_shared_lib_dirs}")

    if len(_shared_lib_dirs) > 0 and not any(
        shared_lib_dir.is_relative_to("lib") for shared_lib_dir in _shared_lib_dirs
    ):
        logging.warning(f"Found directories containing shared libraries outside lib: {_shared_lib_dirs}.")

    _static_libs = list(get_static_libraries(store_path))
    logging.debug(f"Found {len(_static_libs)} static libraries.")
    _static_lib_dirs = {path.parent.relative_to(store_path) for path in _static_libs}
    logging.debug(f"Found {len(_static_lib_dirs)} static library directories: {_static_lib_dirs}")

    if len(_static_lib_dirs) > 0 and not any(
        static_lib_dir.is_relative_to("lib") for static_lib_dir in _static_lib_dirs
    ):
        logging.warning(f"Found directories containing static libraries outside lib: {_static_lib_dirs}.")

    return features


def process_package(package_name: str, package: manifest.Package) -> tuple[str, Package]:
    package_info_kwargs: dict[str, str] = {
        "name": package.name,
        "license": package.license,
        "version": package.version,
    }
    logging.info(f"Package: {package_name} ({package.name})")
    logging.debug(f"License: {package.license}")
    logging.info(f"Version: {package.version}")

    package_arch_kwargs: dict[generic.Architecture, ReleaseFeatures] = {}
    for arch, release in package.get_architectures().items():
        if release is None:
            # Package does not support this architecture.
            continue

        logging.info(f"Architecture: {arch}")
        logging.debug(f"Relative path: {release.relative_path}")
        logging.debug(f"SHA256: {release.sha256}")
        logging.debug(f"MD5: {release.md5}")
        logging.debug(f"Size: {release.size}")

        # Get the store path for the release.
        archive: NixStoreEntry = nix_store_prefetch_file(release)
        unpacked: NixStoreEntry = nix_store_unpack_archive(archive.store_path)
        unpacked_root = unpacked.store_path
        features = get_release_features(unpacked_root)
        package_arch_kwargs[arch] = features

    return package_name, Package.parse_obj(package_info_kwargs | package_arch_kwargs)


def process_manifest(
    manifest: dict[str, manifest.Package],
) -> dict[str, Package]:
    """
    Processes a manifest to predict the outputs of each package.
    """
    with multiprocessing.Pool() as pool:
        return dict(pool.starmap(process_package, manifest.items(), chunksize=1))
