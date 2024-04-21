# NOTE: Open bugs in Pydantic like https://github.com/pydantic/pydantic/issues/8984 prevent the full switch to the type
# keyword introduced in Python 3.12.
import json
import re
from collections.abc import Sequence
from logging import Logger
from typing import Any, Final
from urllib import request

from cuda_redist_lib.logger import get_logger
from cuda_redist_lib.types import (
    RedistName,
    RedistUrlPrefix,
    Version,
    VersionTA,
)

logger: Final[Logger] = get_logger(__name__)


# Returns true if the version should be ignored.
def is_ignored_nvidia_manifest(redist_name: RedistName, version: Version) -> tuple[bool, str]:
    match redist_name:
        # These CUDA manifests are old enough that they don't conform to the same structure as the newer ones.
        case "cuda":
            return (
                version
                in {
                    "11.0.3",
                    "11.1.1",
                    "11.2.0",
                    "11.2.1",
                    "11.2.2",
                    "11.3.0",
                    "11.3.1",
                    "11.4.0",
                    "11.4.1",
                },
                "does not conform to the expected structure",
            )
        # The cuDNN manifests with four-component versions don't have a cuda_variant field.
        # The three-component versions are fine.
        case "cudnn":
            return (
                len(version.split(".")) == 4,  # noqa: PLR2004
                "uses lib directory structure instead of cuda variant",
            )
        case _:
            return (False, "")


def get_nvidia_manifest_versions(redist_name: RedistName) -> Sequence[Version]:
    regex_str = r"""
        href=                # Match 'href='
        ('|")                # Capture a single or double quote
        redistrib_           # Match 'redistrib_'
        (\d+(?:\.\d+){1,3})  # Capture a version number with 2-4 components
        \.json               # Match '.json'
        \1                   # Match the same quote as the first capture group
    """

    # For CUDA, and CUDA only, we take only the latest minor version for each major version.
    # For other packages, like cuDNN, we take the latest patch version for each minor version.
    # An example of why we do this: between patch releases of cuDNN, NVIDIA may not offer support for all
    # architecutres! For instance, cuDNN 8.9.5 supports Jetson, but cuDNN 8.9.6 does not.
    num_components: int = 2 if redist_name == "cuda" else 3
    # Map major and minor component to the tuple of all components and the version string.
    version_dict: dict[tuple[int, ...], tuple[tuple[int, ...], Version]] = {}
    with request.urlopen(f"{RedistUrlPrefix}/{redist_name}/redist/index.html") as response:
        s: str = response.read().decode("utf-8")
        for raw_version_match in re.finditer(regex_str, s, flags=re.VERBOSE):
            raw_version: str = raw_version_match.group(2)
            version = VersionTA.validate_strings(raw_version)

            is_ignored, reason = is_ignored_nvidia_manifest(redist_name, version)
            if is_ignored:
                logger.info("Ignoring manifest %s version %s: %s", redist_name, version, reason)
                continue

            # Take only the latest minor version for each major version.
            components = tuple(map(int, version.split(".")))
            existing_components, _ = version_dict.get(components[:num_components], (None, None))
            if existing_components is None or components > existing_components:
                version_dict[components[:num_components]] = (components, version)

    return [version for _, version in version_dict.values()]


def get_nvidia_manifest(redist_name: RedistName, version: str) -> dict[str, Any]:
    with request.urlopen(f"{RedistUrlPrefix}/{redist_name}/redist/redistrib_{version}.json") as response:
        content_bytes = response.read()
        maybe_obj = json.loads(content_bytes)
        if not isinstance(maybe_obj, dict):
            raise RuntimeError(f"Expected JSON object for manifest {redist_name} {version}, got {type(maybe_obj)}")
        return maybe_obj  # type: ignore
