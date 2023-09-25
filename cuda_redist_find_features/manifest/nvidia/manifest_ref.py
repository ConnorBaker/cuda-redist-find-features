import logging
import re
import time
from functools import singledispatchmethod
from pathlib import Path
from urllib import request

import pydantic
from pydantic import BaseModel, HttpUrl
from typing_extensions import Self

from cuda_redist_find_features.types import Ref
from cuda_redist_find_features.version import Version
from cuda_redist_find_features.version_constraint import VersionConstraint

from .manifest import NvidiaManifest


class NvidiaManifestRef(BaseModel):
    ref: Ref
    version: Version

    def retrieve(self) -> bytes:
        """
        Retrieves the manifest from the specified URL or file path.
        """
        logging.debug(f"Retrieving manifest from {self.ref}...")
        start_time = time.time()
        content_bytes: bytes = self._retrieve(self.ref)
        end_time = time.time()
        logging.debug(f"Retrieved {self.ref} in {end_time - start_time} seconds.")
        return content_bytes

    @singledispatchmethod
    @staticmethod
    def _retrieve(ref: Ref) -> bytes:
        raise NotImplementedError(
            f"Failed to retrieve {ref}: value of type {type(ref)} is not a valid URL or file path"
        )

    @_retrieve.register
    @staticmethod
    def _(ref: HttpUrl) -> bytes:
        with request.urlopen(ref) as response:
            if response.status != 200:
                raise RuntimeError(f"Failed to fetch url {ref}: {response.status} {response.reason}")
            return response.read()

    @_retrieve.register
    @staticmethod
    def _(ref: Path) -> bytes:
        if not (ref.exists() and ref.is_file()):
            raise RuntimeError(f"Failed to fetch file {ref}: No such file exists")
        return ref.read_bytes()

    def parse(self) -> NvidiaManifest:
        logging.info(f"Reading manifest from {self.ref}...")
        start_time = time.time()
        content_bytes: bytes = self.retrieve()
        manifest = NvidiaManifest.parse_raw(content_bytes)
        end_time = time.time()
        logging.info(f"Read {self.ref} in {end_time - start_time} seconds.")
        logging.info(f"Manifest version: {self.version}")
        logging.info(f"Manifest date: {manifest.release_date or 'unknown'}")
        logging.info(f"Manifest label: {manifest.release_label or 'unknown'}")
        logging.info(f"Manifest product: {manifest.release_product or 'unknown'}")
        logging.debug(f"Manifest keys: {manifest.releases().keys()}")

        return manifest

    def download(self, path: Path) -> Path:
        """
        Downloads or copies the manifest to the specified directory.
        """
        path.mkdir(parents=True, exist_ok=True)
        if path.is_file():
            raise ValueError(f"Failed to create directory {path}: A file exists with that name")

        filename: str = f"redistrib_{self.version}.json"
        dest_path: Path = path / filename
        content_bytes: bytes = self.retrieve()
        dest_path.write_bytes(content_bytes)
        return dest_path

    @classmethod
    def _from_url(cls, url: HttpUrl, version_constraint: VersionConstraint) -> list[Self]:
        refs: list[Self] = []
        with request.urlopen(url) as response:
            if response.status != 200:
                raise RuntimeError(f"Failed to fetch url {url}: {response.status} {response.reason}")
            else:
                logging.debug(f"Fetched {url} successfully.")
            s: str = response.read().decode("utf-8")

            regex_str: str
            if version_constraint.version is not None:
                regex_str = f"href=['\"]redistrib_({version_constraint.version}).json['\"]".replace(".", "\\.")
            else:
                regex_str = r'href=[\'"]redistrib_(\d+\.\d+\.\d+(?:.\d+)?)\.json[\'"]'

            logging.debug(f"Searching with regex {regex_str}...")
            for matched in re.finditer(regex_str, s):
                manifest_version = Version.parse(matched.group(1))
                sat, reason = version_constraint.is_satisfied_by(manifest_version)
                if not sat:
                    logging.debug(f"Skipping {manifest_version} because {reason}")
                    continue

                full_url = pydantic.parse_obj_as(HttpUrl, f"{url}/redistrib_{manifest_version}.json")
                refs.append(cls(ref=full_url, version=manifest_version))

        return refs

    @classmethod
    def _from_dir(cls, dir: Path, version_constraint: VersionConstraint) -> list[Self]:
        refs: list[Self] = []
        if not dir.exists():
            raise ValueError(f"Failed to fetch manifests from {dir}: No such directory exists")
        if not dir.is_dir():
            raise ValueError(f"Failed to fetch manifests from {dir}: Not a directory")

        glob_str: str
        if version_constraint.version is not None:
            glob_str = f"redistrib_{version_constraint.version}.json"
        else:
            # NOTE: Use the numbers 0-9 to match any version number and avoid matching redistrib_features_*.json
            glob_str = f"redistrib_[{''.join(map(str,range(0,10)))}]*.json"

        logging.debug(f"Globbing for {glob_str}...")
        for item_path in dir.glob(glob_str):
            if not item_path.is_file():
                logging.debug(f"Skipping {item_path} because it is not a file")
                continue

            manifest_version = Version.parse(item_path.stem.strip("redistrib_"))
            sat, reason = version_constraint.is_satisfied_by(manifest_version)
            if not sat:
                logging.debug(f"Skipping {item_path} because {reason}")
                continue

            refs.append(cls(ref=item_path, version=manifest_version))

        return refs

    @classmethod
    def from_ref(cls, ref: Ref, version_constraint: VersionConstraint) -> list[Self]:
        logging.debug(f"Fetching manifests from {ref}...")
        start_time = time.time()
        refs: list[Self]

        match ref:
            case HttpUrl():
                refs = cls._from_url(ref, version_constraint)
            case Path():
                refs = cls._from_dir(ref, version_constraint)
            case unknown:
                raise ValueError(
                    f"Failed to fetch {ref}: value of type {type(unknown)} is not a valid URL or file path"
                )

        end_time = time.time()
        logging.debug(f"Found {len(refs)} manifests in {end_time - start_time} seconds.")
        return refs
