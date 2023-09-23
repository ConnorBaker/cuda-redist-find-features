# Listing all the imports here ensures that click loads all the subcommands.
from .__main__ import main
from .download_manifests import download_manifests
from .process_manifests import process_manifests

__all__ = ["main", "download_manifests", "process_manifests"]
