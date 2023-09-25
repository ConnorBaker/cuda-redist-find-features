import logging
from dataclasses import dataclass
from pathlib import Path

from .dir import DirDetector


@dataclass
class PythonModuleDetector(DirDetector):
    """
    Detects the presence of python modules in the site-packages directory under lib.
    """

    dir: Path = Path("lib")

    def detect(self, tree: Path) -> bool:
        if not super().detect(tree):
            return False

        lib = tree / self.dir

        # Get the site-packages directory.
        # There should only be one.
        site_package_dirs = [
            subsubdir
            for subdir in lib.iterdir()
            if subdir.is_dir() and subdir.name.startswith("python")
            for subsubdir in subdir.iterdir()
            if subsubdir.is_dir() and subsubdir.name == "site-packages"
        ]

        # If there are no lib subdirs, we can't have python modules.
        if not site_package_dirs:
            logging.info("No site-packages dir found.")
            return False

        # If there are multiple lib subdirs, we can't have python modules.
        if len(site_package_dirs) > 1:
            raise RuntimeError(f"Found multiple site-packages dirs: {site_package_dirs}")

        # Get the python modules.
        site_package_dir = site_package_dirs[0]

        # Python modules must be non-empty.
        if not any(site_package_dir.iterdir()):
            raise RuntimeError(f"Found empty site-packages dir: {site_package_dir}")

        # Get the python modules.
        python_modules = [module for module in site_package_dir.rglob("*.py")]
        has_python_modules = [] != python_modules

        logging.debug(f"Found python modules: {python_modules}")
        logging.info(f"Found python modules: {has_python_modules}")
        return has_python_modules
