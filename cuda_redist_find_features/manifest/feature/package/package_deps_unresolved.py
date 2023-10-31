from typing import Self

from pydantic import HttpUrl

from cuda_redist_find_features.manifest.feature.outputs import FeatureOutputs
from cuda_redist_find_features.manifest.nvidia import NvidiaPackage
from cuda_redist_find_features.types import (
    HttpUrlTA,
    NixStoreEntry,
)
from cuda_redist_find_features.utilities import get_logger

from .package import FeaturePackage

logger = get_logger(__name__)


class FeaturePackageDepsUnresolved(FeaturePackage):
    @classmethod
    def of(cls, url_prefix: HttpUrl, nvidia_package: NvidiaPackage, cleanup: bool = False) -> Self:
        logger.debug("Relative path: %s", nvidia_package.relative_path)
        logger.debug("SHA256: %s", nvidia_package.sha256)
        logger.debug("MD5: %s", nvidia_package.md5)
        logger.debug("Size: %s", nvidia_package.size)

        # Get the store path for the package.
        url = HttpUrlTA.validate_strings(f"{url_prefix}/{nvidia_package.relative_path}")
        archive = NixStoreEntry.from_url(url, nvidia_package.sha256)
        unpacked = archive.unpack_archive()
        unpacked_root = unpacked.store_path

        # Get the features
        outputs = FeatureOutputs.of(unpacked_root)
        # cuda_architectures = CudaArchitecturesDetector().find(unpacked_root) or []
        # needed_libs = NeededLibsDetector().find(unpacked_root) or []
        # provided_libs = ProvidedLibsDetector().find(unpacked_root) or []
        # TODO(@connorbaker): Excluded for now because they are not used downstream.
        # No need to bloat the feature manifests.
        cuda_architectures = []
        needed_libs = []
        provided_libs = []

        if cleanup:
            logger.debug("Cleaning up %s and %s...", archive.store_path, unpacked.store_path)
            unpacked.delete()
            archive.delete()

        return cls(
            outputs=outputs,
            cuda_architectures=cuda_architectures,
            provided_libs=provided_libs,
            needed_libs=needed_libs,
        )
