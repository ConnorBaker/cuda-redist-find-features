import json
import logging
from pathlib import Path
from typing import Any, TypeAlias

from pydantic import BaseModel
from pydantic.tools import parse_obj_as

from cuda_redist_find_features import generic


class Release(BaseModel):
    relative_path: str
    sha256: str
    md5: str
    size: str


Package: TypeAlias = generic.Package[Release]


def parse_manifest(manifest_path: Path) -> dict[str, Package]:
    with manifest_path.open("rb") as manifest_file:
        manifest_json: dict[str, Any] = json.load(manifest_file)
        release_date = manifest_json.pop("release_date")
        manifest_json.pop("release_label", None)
        manifest_json.pop("release_product", None)
        manifest = parse_obj_as(dict[str, Package], manifest_json)
        logging.info(f"Loaded manifest: {manifest_path}")
        logging.info(f"Release date: {release_date}")
        logging.debug(f"Manifest keys: {manifest.keys()}")

        return manifest
