import logging
import subprocess
import time
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

from pydantic import BaseModel, Field

from cuda_redist_find_features import manifest

URL_PREFIX = "https://developer.download.nvidia.com/compute/cuda/redist"


class NixStoreEntry(BaseModel):
    hash: str
    store_path: Path = Field(alias="storePath")


def nix_store_prefetch_file(release: manifest.Release) -> NixStoreEntry:
    """
    Adds a release to the Nix store.

    NOTE: By specifying the hash type and expected hash, we avoid redownloading.
    """
    url: str = f"{URL_PREFIX}/{release.relative_path}"
    package_name: str = release.relative_path.split("/")[-1]
    logging.debug(f"Adding {package_name} to the Nix store...")
    start_time = time.time()
    result = subprocess.run(
        [
            "nix",
            "store",
            "prefetch-file",
            "--json",
            "--hash-type",
            "sha256",
            "--expected-hash",
            release.sha256,
            url,
        ],
        capture_output=True,
        check=True,
    )
    end_time = time.time()
    logging.debug(f"Added {package_name} to the Nix store in {end_time - start_time} seconds.")
    return NixStoreEntry.parse_raw(result.stdout)


def nix_store_unpack_archive(store_path: Path) -> NixStoreEntry:
    """
    Uses nix flake prefetch to unpack an archive.

    NOTE: Only operate in the Nix store to avoid redownloading the archive.
    NOTE: This command is smart enough to not re-unpack archives.
    """
    url: str = f"file://{store_path.as_posix()}"
    logging.debug(f"Unpacking {store_path}...")
    start_time = time.time()
    result = subprocess.run(
        ["nix", "flake", "prefetch", "--json", url],
        capture_output=True,
        check=True,
    )
    end_time = time.time()
    logging.debug(f"Unpacked {store_path} in {end_time - start_time} seconds.")
    return NixStoreEntry.parse_raw(result.stdout)


def nix_store_delete(store_paths: Sequence[Path]) -> None:
    """
    Delete paths from the Nix store.
    """
    posix_paths = [path.as_posix() for path in store_paths]
    formatted_paths = ", ".join(posix_paths)
    logging.debug(f"Deleting {formatted_paths} from the Nix store...")
    start_time = time.time()
    subprocess.run(
        ["nix", "store", "delete", *posix_paths],
        capture_output=True,
        check=True,
    )
    end_time = time.time()
    logging.debug(f"Deleted {formatted_paths} from the Nix store in {end_time - start_time} seconds.")


def is_nonempty(it: Iterable[Any]) -> bool:
    """
    Returns True if the iterable is nonempty.
    """
    return any(True for _ in it)


def file_paths_matching(path: Path, globs: Iterable[str]) -> Iterator[Path]:
    """
    Returns a list of files matching the given globs in the directory tree of the given path.
    """
    return (entry for glob in globs for entry in path.rglob(glob) if entry.is_file())
