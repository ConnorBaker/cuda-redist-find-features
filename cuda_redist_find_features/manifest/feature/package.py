import logging

from pydantic import BaseModel, Field, HttpUrl, parse_obj_as
from typing_extensions import Self

from cuda_redist_find_features.nix import (
    NixStoreEntry,
    nix_store_delete,
    nix_store_prefetch_file,
    nix_store_unpack_archive,
)

from ..nvidia import NvidiaPackage
from .cuda_architectures import FeatureCudaArchitectures
from .needed_libs import FeatureNeededLibs
from .outputs import FeatureOutputs
from .provided_libs import FeatureProvidedLibs


class FeaturePackage(BaseModel):
    """
    Describes the different features a package can have.

    A package is a release for a specific architecture.
    """

    outputs: FeatureOutputs
    cuda_architectures: FeatureCudaArchitectures = Field(alias="cudaArchitectures")
    provided_libs: FeatureProvidedLibs = Field(alias="providedLibs")
    needed_libs: FeatureNeededLibs = Field(alias="neededLibs")
    # There are just way too many headers to list them all.
    # provided_headers: FeatureProvidedHeaders = Field(alias="providedHeaders")
    # libs_provided: FeatureLibsProvided
    # libs_needed: FeatureLibsNeeded

    @classmethod
    def of(cls, url_prefix: HttpUrl, nvidia_package: NvidiaPackage, cleanup: bool = False) -> Self:
        logging.debug(f"Relative path: {nvidia_package.relative_path}")
        logging.debug(f"SHA256: {nvidia_package.sha256}")
        logging.debug(f"MD5: {nvidia_package.md5}")
        logging.debug(f"Size: {nvidia_package.size}")

        # Get the store path for the package.
        url = parse_obj_as(HttpUrl, f"{url_prefix}/{nvidia_package.relative_path}")
        archive: NixStoreEntry = nix_store_prefetch_file(url, nvidia_package.sha256)
        unpacked: NixStoreEntry = nix_store_unpack_archive(archive.store_path)
        unpacked_root = unpacked.store_path

        outputs = FeatureOutputs.of(unpacked_root)
        cuda_architectures = FeatureCudaArchitectures.of(unpacked_root)
        needed_libs = FeatureNeededLibs.of(unpacked_root)
        provided_libs = FeatureProvidedLibs.of(unpacked_root)
        # provided_headers = FeatureProvidedHeaders.of(unpacked_root)
        # libs_provided = FeatureLibsProvided.of(unpacked_root)
        # libs_needed = FeatureLibsNeeded.of(unpacked_root)

        if cleanup:
            logging.debug(f"Cleaning up {archive.store_path} and {unpacked.store_path}...")
            nix_store_delete([archive.store_path, unpacked.store_path])

        return cls(
            outputs=outputs, cudaArchitectures=cuda_architectures, providedLibs=provided_libs, neededLibs=needed_libs
        )
