from dataclasses import dataclass
from typing import Annotated, final

from ._package_name import PackageName
from ._platform import Platform
from ._pydantic import PydanticFrozenField
from ._version import Version


@final
@dataclass(frozen=True, order=True, slots=True)
class PackageId:
    """
    Useful for uniquely identifying a package in a manifest, e.g. for use as a key in a mapping for a collapsed
    manifest.
    """

    platform: Platform
    package_name: PackageName
    version: Annotated[
        Version,
        PydanticFrozenField(
            description="The version of the package or the manifest from which it was retrieved.",
            examples=["11.2.0", "2.17"],
        ),
    ]
