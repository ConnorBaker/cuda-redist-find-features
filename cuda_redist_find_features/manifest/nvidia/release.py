from typing import Mapping, Sequence, cast, get_args

from pydantic import BaseModel

from cuda_redist_find_features.types import Architecture

from .package import NvidiaPackage


class NvidiaRelease(BaseModel):
    """
    Represents a release in the manifest.

    A release is a collection of packages of the same library for different architectures.

    Beyond the fields provided as properties, the package may also have the following fields,
    depending on the architectures supported by the package:

    - `linux-aarch64`
    - `linux-ppc64le`
    - `linux-sbsa`
    - `linux-x86_64`
    - `windows-x86_64`
    """

    __root__: Mapping[str, str | NvidiaPackage]

    def packages(self) -> dict[Architecture, NvidiaPackage]:
        """
        Returns a mapping of architecture to package.
        """
        packages: dict[Architecture, NvidiaPackage] = {}
        for arch in cast(Sequence[Architecture], get_args(Architecture)):
            package = self.__root__.get(arch)
            match package:
                case None:
                    continue
                case NvidiaPackage():
                    packages[arch] = package
                case unknown:
                    raise RuntimeError(f"Expected {arch} to be a package, but got {type(unknown)}")

        return packages

    @property
    def name(self) -> str:
        name = self.__root__.get("name")
        match name:
            case None:
                raise RuntimeError(f"Expected release to have a name, but got {name}")
            case str():
                return name
            case unknown:
                raise RuntimeError(f"Expected release name to be a string, but got {type(unknown)}")

    @property
    def license(self) -> str:
        license = self.__root__.get("license")
        match license:
            case None:
                raise RuntimeError(f"Expected release to have a license, but got {license}")
            case str():
                return license
            case unknown:
                raise RuntimeError(f"Expected release license to be a string, but got {type(unknown)}")

    @property
    def version(self) -> str:
        version = self.__root__.get("version")
        match version:
            case None:
                raise RuntimeError(f"Expected release to have a version, but got {version}")
            case str():
                return version
            case unknown:
                raise RuntimeError(f"Expected release version to be a string, but got {type(unknown)}")

    @property
    def license_path(self) -> None | str:
        license_path = self.__root__.get("license_path")
        match license_path:
            case None | str():
                return license_path
            case unknown:
                raise RuntimeError(f"Expected release license path to be a string, but got {type(unknown)}")
