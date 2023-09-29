import logging
from collections.abc import Mapping, Sequence
from typing import Self

from pydantic import HttpUrl
from pydantic.alias_generators import to_camel

from cuda_redist_find_features.nix import (
    NixStoreEntry,
    nix_store_delete,
    nix_store_prefetch_file,
    nix_store_unpack_archive,
)
from cuda_redist_find_features.types import FF, SFBM, SFF, CudaArch, HttpUrlTA, LibSoName

from ..nvidia import NvidiaPackage
from .detectors import CudaArchitecturesDetector, NeededLibsDetector, ProvidedLibsDetector
from .outputs import FeatureOutputs


class FeaturePackage(SFBM, alias_generator=to_camel):
    """
    Describes the different features a package can have.

    A package is a release for a specific architecture.
    """

    outputs: FeatureOutputs = SFF(
        description="The Nix outputs of the package.",
        examples=["lib", "dev", "static"],
    )
    cuda_architectures: Sequence[CudaArch] | Mapping[str, Sequence[CudaArch]] = FF(
        description=(
            """
            The CUDA architectures supported by the package.
            This is either a list of architectures or a mapping from subdirectory name to list of architectures.
            """
        ),
    )
    provided_libs: Sequence[LibSoName] | Mapping[str, Sequence[LibSoName]] = FF(
        description=(
            """
            The libraries provided by the package.
            This is either a list of libraries or a mapping from subdirectory name to list of libraries.
            """
        ),
    )
    needed_libs: Sequence[LibSoName] | Mapping[str, Sequence[LibSoName]] = FF(
        description=(
            """
            The libraries needed by the package.
            This is either a list of libraries or a mapping from subdirectory name to list of libraries.
            """
        ),
    )
    # There are just way too many headers to list them all.
    # provided_headers: FeatureProvidedHeaders = Field(alias="providedHeaders")

    @classmethod
    def of(cls, url_prefix: HttpUrl, nvidia_package: NvidiaPackage, cleanup: bool = False) -> Self:
        logging.debug(f"Relative path: {nvidia_package.relative_path}")
        logging.debug(f"SHA256: {nvidia_package.sha256}")
        logging.debug(f"MD5: {nvidia_package.md5}")
        logging.debug(f"Size: {nvidia_package.size}")

        # Get the store path for the package.
        url = HttpUrlTA.validate_python(f"{url_prefix}/{nvidia_package.relative_path}")
        archive: NixStoreEntry = nix_store_prefetch_file(url, nvidia_package.sha256)
        unpacked: NixStoreEntry = nix_store_unpack_archive(archive.store_path)
        unpacked_root = unpacked.store_path

        # Get the features
        outputs = FeatureOutputs.of(unpacked_root)
        cuda_architectures = CudaArchitecturesDetector().find(unpacked_root) or []
        needed_libs = NeededLibsDetector().find(unpacked_root) or []
        provided_libs = ProvidedLibsDetector().find(unpacked_root) or []

        if cleanup:
            logging.debug(f"Cleaning up {archive.store_path} and {unpacked.store_path}...")
            nix_store_delete([archive.store_path, unpacked.store_path])

        return cls(
            outputs=outputs,
            cuda_architectures=cuda_architectures,
            provided_libs=provided_libs,
            needed_libs=needed_libs,
        )
