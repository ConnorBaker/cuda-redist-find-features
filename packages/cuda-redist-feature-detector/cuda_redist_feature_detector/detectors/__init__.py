from .cuda_architectures import CudaArchitecturesDetector
from .dir import DirDetector
from .dynamic_library import DynamicLibraryDetector
from .executable import ExecutableDetector
from .header import HeaderDetector
from .lib_subdirs import LibSubdirsDetector
from .needed_libs import NeededLibsDetector
from .provided_libs import ProvidedLibsDetector
from .python_module import PythonModuleDetector
from .static_library import StaticLibraryDetector
from .stubs import StubsDetector

__all__ = [
    "CudaArchitecturesDetector",
    "DirDetector",
    "DynamicLibraryDetector",
    "ExecutableDetector",
    "HeaderDetector",
    "LibSubdirsDetector",
    "NeededLibsDetector",
    "ProvidedLibsDetector",
    "PythonModuleDetector",
    "StaticLibraryDetector",
    "StubsDetector",
]
