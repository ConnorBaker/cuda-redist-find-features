from .cuda_architectures import CudaArchitecturesDetector
from .dir import DirDetector
from .dynamic_library import DynamicLibraryDetector
from .executable import ExecutableDetector
from .header import HeaderDetector
from .needed_libs import NeededLibsDetector
from .provided_libs import ProvidedLibsDetector
from .python_module import PythonModuleDetector
from .static_library import StaticLibraryDetector

__all__ = [
    "DirDetector",
    "DynamicLibraryDetector",
    "ExecutableDetector",
    "HeaderDetector",
    "PythonModuleDetector",
    "StaticLibraryDetector",
    "CudaArchitecturesDetector",
    "ProvidedLibsDetector",
    "NeededLibsDetector",
]
