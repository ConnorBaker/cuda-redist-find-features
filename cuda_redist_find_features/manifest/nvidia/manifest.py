from typing import Mapping

from pydantic import BaseModel

from .release import NvidiaRelease


class NvidiaManifest(BaseModel):
    """
    Represents the manifest file containing releases.
    """

    __root__: Mapping[str, str | NvidiaRelease]

    def releases(self) -> dict[str, NvidiaRelease]:
        """
        Returns a mapping of package name to release.
        """
        return {name: release for name, release in self.__root__.items() if isinstance(release, NvidiaRelease)}

    @property
    def release_date(self) -> None | str:
        release_date = self.__root__.get("release_date")
        match release_date:
            case None | str():
                return release_date
            case unknown:
                raise RuntimeError(f"Expected manifest release date to be a string, but got {type(unknown)}")

    @property
    def release_label(self) -> None | str:
        release_label = self.__root__.get("release_label")
        match release_label:
            case None | str():
                return release_label
            case unknown:
                raise RuntimeError(f"Expected manifest release label to be a string, but got {type(unknown)}")

    @property
    def release_product(self) -> None | str:
        release_product = self.__root__.get("release_product")
        match release_product:
            case None | str():
                return release_product
            case unknown:
                raise RuntimeError(f"Expected manifest release product to be a string, but got {type(unknown)}")
