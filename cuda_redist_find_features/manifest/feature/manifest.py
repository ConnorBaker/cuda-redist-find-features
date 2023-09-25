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
        executor: None | ProcessPoolExecutor = None,
    ) -> Self:
        manifest_release_kwargs: dict[str, FeatureRelease] = {}
        if executor is not None:
            futures: dict[str, Future[FeatureRelease]] = {}
            for name, nvidia_package in nvidia_manifest.releases().items():
                futures[name] = executor.submit(FeatureRelease.of, url_prefix, nvidia_package, cleanup)

            manifest_release_kwargs = {name: future.result() for name, future in futures.items()}

        else:
            manifest_release_kwargs = {
                name: FeatureRelease.of(url_prefix, nvidia_package, cleanup)
                for name, nvidia_package in nvidia_manifest.releases().items()
            }

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
