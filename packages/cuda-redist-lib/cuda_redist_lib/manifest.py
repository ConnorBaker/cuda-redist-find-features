# NOTE: Open bugs in Pydantic like https://github.com/pydantic/pydantic/issues/8984 prevent the full switch to the type
# keyword introduced in Python 3.12.
import json
import re
from collections.abc import Sequence
from typing import (
    Any,
)
from urllib import request

from cuda_redist_lib.types import (
    RedistName,
    RedistUrlPrefix,
    Version,
    VersionTA,
)


def get_nvidia_manifest_versions(redist_name: RedistName) -> Sequence[Version]:
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
        return [VersionTA.validate_strings(matched.group(2)) for matched in re.finditer(regex_str, s, flags=re.VERBOSE)]


def get_nvidia_manifest(redist_name: RedistName, version: str) -> dict[str, Any]:
    with request.urlopen(f"{RedistUrlPrefix}/{redist_name}/redist/redistrib_{version}.json") as response:
        content_bytes = response.read()
        maybe_obj = json.loads(content_bytes)
        if not isinstance(maybe_obj, dict):
            raise RuntimeError(f"Expected JSON object for manifest {redist_name} {version}, got {type(maybe_obj)}")
        return maybe_obj  # type: ignore


# Returns true if the version should be ignored.
def is_ignored_nvidia_manifest(redist_name: RedistName, version: Version) -> bool:
    match redist_name:
        # These CUDA manifests are old enough that they don't conform to the same structure as the newer ones.
        case "cuda":
            return version in {
                "11.0.3",
                "11.1.1",
                "11.2.0",
                "11.2.1",
                "11.2.2",
                "11.3.0",
                "11.3.1",
                "11.4.0",
                "11.4.1",
            }
        # The cuDNN manifests with four-component versions don't have a cuda_variant field.
        # The three-component versions are fine.
        case "cudnn":
            return len(version.split(".")) == 4  # noqa: PLR2004
        case _:
            return False
