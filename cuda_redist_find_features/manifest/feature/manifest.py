from concurrent.futures import Future, ProcessPoolExecutor
from pathlib import Path
from typing import Self

from pydantic import HttpUrl

from cuda_redist_find_features.types import SFMRM, PackageName

from ..nvidia import NvidiaManifest
from .release import FeatureRelease


class FeatureManifest(SFMRM[PackageName, FeatureRelease]):
    """
    Represents the manifest file containing releases.
    """

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
            for name, nvidia_package in nvidia_manifest.releases.items():
                futures[name] = executor.submit(FeatureRelease.of, url_prefix, nvidia_package, cleanup)

            manifest_release_kwargs = {name: future.result() for name, future in futures.items()}

        else:
            manifest_release_kwargs = {
                name: FeatureRelease.of(url_prefix, nvidia_package, cleanup)
                for name, nvidia_package in nvidia_manifest.releases.items()
            }

        return cls.model_validate(manifest_release_kwargs)

    def write(self, path: Path) -> None:
        """
        Writes the manifest to the given path.
        """
        with path.open("w") as f:
            f.write(self.model_dump_json(by_alias=True, exclude_none=True, indent=2))
            f.write("\n")
            f.flush()
