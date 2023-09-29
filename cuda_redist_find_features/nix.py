import logging
import subprocess
import time
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated

from annotated_types import Predicate
from pydantic import FilePath, HttpUrl
from pydantic.alias_generators import to_camel

from .types import SFBM, Sha256, validate_call


class NixStoreEntry(SFBM, alias_generator=to_camel):
    hash: str
    store_path: Annotated[Path, Predicate(Path.exists)]


@validate_call
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
            str(url),
        ],
        capture_output=True,
        check=True,
    )
    end_time = time.time()
    logging.info(f"Added {url} to the Nix store in {end_time - start_time} seconds.")
    return NixStoreEntry.model_validate_json(result.stdout, strict=False)


@validate_call
def nix_store_unpack_archive(store_path: FilePath) -> NixStoreEntry:
    """
    Uses nix flake prefetch to unpack an archive.

    NOTE: Only operate in the Nix store to avoid redownloading the archive.
    NOTE: This command is smart enough to not re-unpack archives.
    """
    uri: str = store_path.as_uri()
    logging.info(f"Unpacking {store_path}...")
    start_time = time.time()
    result = subprocess.run(
        ["nix", "flake", "prefetch", "--json", uri],
        capture_output=True,
        check=True,
    )
    end_time = time.time()
    logging.info(f"Unpacked {store_path} in {end_time - start_time} seconds.")
    return NixStoreEntry.model_validate_json(result.stdout)


@validate_call
def nix_store_delete(store_paths: Iterable[Path]) -> None:
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
