from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Any, TypeAlias
from urllib import request

import pydantic
from pydantic import BaseModel, HttpUrl
from pydantic.tools import parse_obj_as
from typing_extensions import Self

from cuda_redist_find_features import generic
from cuda_redist_find_features.version import Version
from cuda_redist_find_features.version_constraint import VersionConstraint


class Release(BaseModel):
    relative_path: str
    sha256: str
    md5: str
    size: str


Ref: TypeAlias = HttpUrl | Path
Package: TypeAlias = generic.Package[Release]


class ManifestRef(BaseModel):
    ref: Ref
    version: Version

    def read_bytes(self) -> bytes:
        logging.debug(f"Reading manifest from {self.ref}...")
        start_time = time.time()
        content_bytes: bytes

        match self.ref:
            case HttpUrl():
                with request.urlopen(self.ref) as response:
                    if response.status != 200:
                        err_msg = f"Failed to fetch url {self.ref}: {response.status} {response.reason}"
                        logging.error(err_msg)
                        raise RuntimeError(err_msg)
                    content_bytes = response.read()
            case Path():
                if not (self.ref.exists() and self.ref.is_file()):
                    err_msg = f"Failed to fetch file {self.ref}: No such file exists"
                    logging.error(err_msg)
                    raise RuntimeError(err_msg)
                content_bytes = self.ref.read_bytes()
            case unknown:
                err_msg = f"Failed to fetch {self.ref}: value of type {type(unknown)} a valid URL or file path"
                logging.error(err_msg)
                raise ValueError(err_msg)

        end_time = time.time()
        logging.debug(f"Read {self.ref} in {end_time - start_time} seconds.")
        return content_bytes

    def parse_manifest(self) -> dict[str, Package]:
        content_bytes: bytes = self.read_bytes()
        manifest_json: dict[str, Any] = json.loads(content_bytes)
        release_date = manifest_json.pop("release_date", None)
        manifest_json.pop("release_label", None)
        manifest_json.pop("release_product", None)
        manifest = parse_obj_as(dict[str, Package], manifest_json)
        logging.info(f"Loaded manifest: {self.ref}")
        logging.info(f"Version: {self.version}")
        logging.info(f"Release date: {release_date or 'unknown'}")
        logging.debug(f"Manifest keys: {manifest.keys()}")

        return manifest

    def download(self, path: Path) -> Path:
        """
        Downloads the manifest to the specified directory.
        """
        path.mkdir(parents=True, exist_ok=True)
        if path.is_file():
            err_msg = f"Failed to create directory {path}: A file exists with that name"
            logging.error(err_msg)
            raise ValueError(err_msg)

        filename: str = f"redistrib_{self.version}.json"
        dest_path: Path = path / filename
        content_bytes: bytes = self.read_bytes()
        dest_path.write_bytes(content_bytes)
        return dest_path

    @classmethod
    def _from_url(cls, url: HttpUrl, version_constraint: VersionConstraint) -> list[Self]:
        refs: list[Self] = []
        with request.urlopen(url) as response:
            if response.status != 200:
                err_msg = f"Failed to fetch url {url}: {response.status} {response.reason}"
                logging.error(err_msg)
                raise RuntimeError(err_msg)
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
            err_msg = f"Failed to fetch manifests from {dir}: No such directory exists"
            logging.error(err_msg)
            raise ValueError(err_msg)
        if not dir.is_dir():
            err_msg = f"Failed to fetch manifests from {dir}: Not a directory"
            logging.error(err_msg)
            raise ValueError(err_msg)

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
                err_msg = f"Failed to fetch {ref}: value of type {type(unknown)} is not a valid URL or file path"
                logging.error(err_msg)
                raise ValueError(err_msg)

        end_time = time.time()
        logging.debug(f"Found {len(refs)} manifests in {end_time - start_time} seconds.")
        return refs
