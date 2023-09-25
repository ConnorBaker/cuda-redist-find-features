import logging
from concurrent.futures import Future, ProcessPoolExecutor
from pathlib import Path
from typing import Mapping

from pydantic import BaseModel, HttpUrl
from typing_extensions import Self

from ..nvidia import NvidiaManifest
from .release import FeatureRelease


class FeatureManifest(BaseModel):
    """
    Represents the manifest file containing releases.
    """

    __root__: Mapping[str, FeatureRelease]

    @classmethod
    def of(
        cls,
        url_prefix: HttpUrl,
        nvidia_manifest: NvidiaManifest,
        cleanup: bool = False,
        no_parallel: bool = False,
    ) -> Self:
        logging.info(f"Release date: {nvidia_manifest.release_date}")
        logging.info(f"Release label: {nvidia_manifest.release_label}")
        logging.info(f"Release product: {nvidia_manifest.release_product}")

        manifest_release_kwargs: dict[str, FeatureRelease] = {}
        if no_parallel:
            for name, nvidia_package in nvidia_manifest.releases().items():
                logging.info(f"Package: {name}")
                manifest_release_kwargs[name] = FeatureRelease.of(url_prefix, nvidia_package, cleanup)
        else:
            with ProcessPoolExecutor() as executor:
                futures: dict[str, Future[FeatureRelease]] = {}
                for name, nvidia_package in nvidia_manifest.releases().items():
                    logging.info(f"Package: {name}")
                    futures[name] = executor.submit(FeatureRelease.of, url_prefix, nvidia_package, cleanup)

                for name, future in futures.items():
                    manifest_release_kwargs[name] = future.result()

        return cls.parse_obj(manifest_release_kwargs)

    def releases(self) -> dict[str, FeatureRelease]:
        """
        Returns a mapping of package name to release.
        """
        return {name: release for name, release in self.__root__.items() if isinstance(release, FeatureRelease)}

    def write(self, path: Path) -> None:
        """
        Writes the manifest to the given path.
        """
        with path.open("w") as f:
            f.write(self.json(by_alias=True, exclude_none=True, indent=2, sort_keys=True))
            f.write("\n")
            f.flush()
