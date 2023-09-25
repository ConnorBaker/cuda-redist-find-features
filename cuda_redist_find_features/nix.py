import logging
import subprocess
import time
from pathlib import Path
from typing import Sequence

from pydantic import BaseModel, Field, HttpUrl, parse_raw_as

from .types import Sha256


class NixStoreEntry(BaseModel):
    hash: str
    store_path: Path = Field(alias="storePath")


def nix_store_prefetch_file(url: HttpUrl, sha256: Sha256) -> NixStoreEntry:
    """
    Adds a release to the Nix store.

    NOTE: By specifying the hash type and expected hash, we avoid redownloading.
    """
    logging.info(f"Adding {url} to the Nix store...")
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
            sha256,
            url,
        ],
        capture_output=True,
        check=True,
    )
    end_time = time.time()
    logging.info(f"Added {url} to the Nix store in {end_time - start_time} seconds.")
    return NixStoreEntry.parse_raw(result.stdout)


def nix_store_unpack_archive(store_path: Path) -> NixStoreEntry:
    """
    Uses nix flake prefetch to unpack an archive.

    NOTE: Only operate in the Nix store to avoid redownloading the archive.
    NOTE: This command is smart enough to not re-unpack archives.
    """
    url: str = f"file://{store_path.as_posix()}"
    logging.info(f"Unpacking {store_path}...")
    start_time = time.time()
    result = subprocess.run(
        ["nix", "flake", "prefetch", "--json", url],
        capture_output=True,
        check=True,
    )
    end_time = time.time()
    logging.info(f"Unpacked {store_path} in {end_time - start_time} seconds.")
    return parse_raw_as(NixStoreEntry, result.stdout)


def nix_store_delete(store_paths: Sequence[Path]) -> None:
    """
    Delete paths from the Nix store.
    """
    posix_paths = [path.as_posix() for path in store_paths]
    formatted_paths = ", ".join(posix_paths)
    logging.info(f"Deleting {formatted_paths} from the Nix store...")
    start_time = time.time()
    subprocess.run(
        ["nix", "store", "delete", *posix_paths],
        capture_output=True,
        check=True,
    )
    end_time = time.time()
    logging.info(f"Deleted {formatted_paths} from the Nix store in {end_time - start_time} seconds.")
