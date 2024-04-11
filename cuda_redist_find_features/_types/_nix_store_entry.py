import subprocess
import time
from pathlib import Path
from typing import Annotated, Self

from annotated_types import Predicate
from pydantic import HttpUrl
from pydantic.alias_generators import to_camel

from cuda_redist_find_features.utilities import get_logger

from ._pydantic import PydanticObject
from ._sha256 import Sha256
from ._sri_hash import SriHash

logger = get_logger(__name__)


class NixStoreEntry(PydanticObject, alias_generator=to_camel):
    hash: SriHash
    store_path: Annotated[Path, Predicate(Path.exists)]

    @classmethod
    def from_url(cls, url: HttpUrl, sha256: Sha256) -> Self:
        """
        Adds a release to the Nix store.

        NOTE: By specifying the hash type and expected hash, we avoid redownloading.
        """
        logger.info("Adding %s to the Nix store...", url)
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
        logger.info("Added %s to the Nix store in %d seconds.", url, end_time - start_time)
        return cls.model_validate_json(result.stdout, strict=False)

    def unpack_archive(self) -> Self:
        """
        Uses nix flake prefetch to unpack an archive and return the recursive NAR hash.

        NOTE: Only operate in the Nix store to avoid redownloading the archive.
        NOTE: This command is smart enough to not re-unpack archives.
        """
        uri: str = self.store_path.as_uri()
        logger.info("Unpacking %s...", uri)
        start_time = time.time()
        result = subprocess.run(
            ["nix", "flake", "prefetch", "--json", uri],
            capture_output=True,
            check=True,
        )
        end_time = time.time()
        logger.info("Unpacked %s in %d seconds.", uri, end_time - start_time)
        return self.model_validate_json(result.stdout)

    def delete(self) -> None:
        """
        Delete paths from the Nix store.
        """
        str_path: str = self.store_path.as_posix()
        logger.info("Deleting %s from the Nix store...", str_path)
        start_time = time.time()
        subprocess.run(
            ["nix", "store", "delete", str_path],
            capture_output=True,
            check=True,
        )
        end_time = time.time()
        logger.info("Deleted %s from the Nix store in %d seconds.", str_path, end_time - start_time)
