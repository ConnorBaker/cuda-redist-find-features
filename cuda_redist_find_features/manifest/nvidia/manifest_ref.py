from __future__ import annotations

import logging
import re
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Generic, TypeVar
from urllib import request

from pydantic import BaseModel, DirectoryPath, FilePath, HttpUrl
from pydantic_core import Url

from cuda_redist_find_features.types import FF, SFF, HttpUrlTA, validate_call
from cuda_redist_find_features.version import Version
from cuda_redist_find_features.version_constraint import VersionConstraint

from .manifest import NvidiaManifest

_T = TypeVar("_T", FilePath, HttpUrl)


class NvidiaManifestRef(BaseModel, Generic[_T]):
    ref: _T = FF(
        description="A reference to a manifest at a local file or a URL.",
        examples=[
            "https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.7.0.json",
            "cutensor_manifests/redistrib_1.7.0.json",
        ],
    )
    version: Version = SFF(
        description="The version of the manifest.",
        examples=["1.7.0"],
    )

    @validate_call
    def retrieve(self) -> bytes:
        logging.info(f"Reading manifest from {self.ref}...")
        match self.ref:
            case Url():
                with request.urlopen(str(self.ref)) as response:
                    if response.status != 200:  # noqa: PLR2004
                        raise RuntimeError(f"Failed to fetch url {self.ref}: {response.status} {response.reason}")
                    return response.read()
            case Path():
                return self.ref.read_bytes()

    @validate_call
    def parse(self) -> NvidiaManifest:
        content_bytes: bytes = self.retrieve()
        manifest = NvidiaManifest.model_validate_json(content_bytes)
        logging.info(f"Manifest version: {self.version}")
        logging.info(f"Manifest date: {manifest.release_date or 'unknown'}")
        logging.info(f"Manifest label: {manifest.release_label or 'unknown'}")
        logging.info(f"Manifest product: {manifest.release_product or 'unknown'}")
        return manifest

    def download(self, dir: DirectoryPath) -> NvidiaManifestRef[FilePath]:
        """
        Downloads or copies the manifest referenced by `self` to the specified directory.
        """
        filename: str = f"redistrib_{self.version}.json"
        dest_path: Path = dir / filename
        if dest_path.exists():
            logging.warning(f"Manifest {dest_path} already exists, overwriting")
        content_bytes: bytes = self.retrieve()
        dest_path.write_bytes(content_bytes)
        logging.info(f"Wrote manifest to {dest_path}.")
        return NvidiaManifestRef(ref=dest_path, version=self.version)

    @staticmethod
    def _from_url(url: HttpUrl, version_constraint: VersionConstraint) -> Sequence[NvidiaManifestRef[HttpUrl]]:
        refs: list[NvidiaManifestRef[HttpUrl]] = []

        if version_constraint.version is not None:
            regex_str = f"href=['\"]redistrib_({version_constraint.version}).json['\"]".replace(".", "\\.")
        else:
            regex_str = r'href=[\'"]redistrib_(\d+\.\d+\.\d+(?:.\d+)?)\.json[\'"]'

        with request.urlopen(str(url)) as response:
            if response.status != 200:  # noqa: PLR2004
                raise RuntimeError(f"Failed to fetch url {url}: {response.status} {response.reason}")

            s: str = response.read().decode("utf-8")
            logging.debug(f"Searching with regex {regex_str}...")
            for matched in re.finditer(regex_str, s):
                manifest_version = Version.model_validate_strings(matched.group(1))
                if not version_constraint.is_satisfied_by(manifest_version):
                    continue

                full_url = HttpUrlTA.validate_python(f"{url}/redistrib_{manifest_version}.json")
                refs.append(NvidiaManifestRef(ref=full_url, version=manifest_version))

        return refs

    @staticmethod
    def _from_dir(dir: DirectoryPath, version_constraint: VersionConstraint) -> Sequence[NvidiaManifestRef[FilePath]]:
        filename_prefix = "redistrib_"
        filename_suffix = ".json"

        if version_constraint.version is not None:
            version_glob_str = str(version_constraint.version)
        else:
            # Use the numbers 0-9 to match any version number and avoid matching redistrib_features_*.json
            version_glob_str = f"[{''.join(map(str,range(0,10)))}]*"

        glob_str = filename_prefix + version_glob_str + filename_suffix

        refs: list[NvidiaManifestRef[FilePath]] = []
        for file in dir.glob(glob_str):
            manifest_version = Version.model_validate_strings(file.stem.strip(filename_prefix))
            if version_constraint.is_satisfied_by(manifest_version):
                refs.append(NvidiaManifestRef(ref=file, version=manifest_version))

        logging.debug(f"Globbing for {glob_str}...")
        return refs

    @staticmethod
    def from_ref(ref: _T, version_constraint: VersionConstraint) -> Sequence[NvidiaManifestRef[_T]]:
        logging.debug(f"Fetching manifests from {ref}...")
        start_time = time.time()
        # NOTE: If we move the return statement outside the match, pyright complains that the return type is not
        # compatible with the type annotation.
        match ref:
            case Url():
                refs = NvidiaManifestRef._from_url(ref, version_constraint)
                end_time = time.time()
                logging.debug(f"Found {len(refs)} manifests in {end_time - start_time} seconds.")
                return refs
            case Path():
                refs = NvidiaManifestRef._from_dir(ref, version_constraint)
                end_time = time.time()
                logging.debug(f"Found {len(refs)} manifests in {end_time - start_time} seconds.")
                return refs
