import logging
from dataclasses import dataclass
from pathlib import Path

from typing_extensions import override

from .dir import DirDetector
from .types import FeatureDetector
from .utilities import cached_path_rglob


@dataclass
class PythonModuleDetector(FeatureDetector[list[Path]]):
    """
    Detects the presence of python modules in the `site-packages` directory under `lib`.
    """

    @override
    def find(self, store_path: Path) -> None | list[Path]:
        """
        Finds paths of python modules under `site-packages` directory under `lib` within the given Nix store path.
        """
        lib_dir = DirDetector(Path("lib")).find(store_path)
        if lib_dir is None:
            return None

        # Get the site-packages directory.
        # There should only be one.
        site_packages_dirs = [
            subsubdir
            for subdir in lib_dir.iterdir()
            if subdir.is_dir() and subdir.name.startswith("python")
            for subsubdir in subdir.iterdir()
            if subsubdir.is_dir() and subsubdir.name == "site-packages"
        ]

        # If there are no lib subdirs, we can't have python modules.
        if not site_packages_dirs:
            logging.debug("No site-packages dir found.")
            return None

        # If there are multiple lib subdirs, we can't have python modules.
        if len(site_packages_dirs) > 1:
            raise RuntimeError(f"Found multiple site-packages dirs: {site_packages_dirs}")

        # Get the python modules.
        site_packages_dir = site_packages_dirs[0]

        # Python modules must be non-empty.
        if not any(site_packages_dir.iterdir()):
            raise RuntimeError(f"Found empty site-packages dir: {site_packages_dir}")

        # Get the python modules.
        python_modules = cached_path_rglob(site_packages_dir, "*.py", files_only=True)
        if [] != python_modules:
            logging.debug(f"Found python modules: {python_modules}")
            return python_modules

        return None
