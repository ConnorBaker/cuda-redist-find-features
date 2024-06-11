from pathlib import Path
from typing import Self

from cuda_redist_lib.extra_pydantic import PydanticSequence

from cuda_redist_feature_detector.detectors import (
    DirDetector,
    DynamicLibraryDetector,
    ExecutableDetector,
    StaticLibraryDetector,
    StubsDetector,
)


class FeatureOutputs(PydanticSequence[str]):
    """
    Describes the different outputs a release can have.

    A number of these checks are taken from
    https://github.com/NixOS/nixpkgs/blob/d4d822f526f1f72a450da88bf35abe132181170f/pkgs/build-support/setup-hooks/multiple-outputs.sh.
    """

    @classmethod
    def of(cls, store_path: Path) -> Self:
        outputs: list[str] = ["out"]
        if cls.check_bin(store_path):
            outputs.append("bin")
        if cls.check_dev(store_path):
            outputs.append("dev")
        if cls.check_doc(store_path):
            outputs.append("doc")
        if cls.check_lib(store_path):
            outputs.append("lib")
        if cls.check_python(store_path):
            outputs.append("python")
        if cls.check_sample(store_path):
            outputs.append("sample")
        if cls.check_static(store_path):
            outputs.append("static")
        if cls.check_stubs(store_path):
            outputs.append("stubs")
        return cls(outputs)

    @staticmethod
    def check_bin(store_path: Path) -> bool:
        """
        A `bin` output requires that we have a non-empty `bin` directory containing at least one file with the
        executable bit set.
        """
        return ExecutableDetector().detect(store_path)

    @staticmethod
    def check_dev(store_path: Path) -> bool:
        """
        A `dev` output requires that we have at least one of the following non-empty directories:

        - `include`
        - `lib/pkgconfig`
        - `share/pkgconfig`
        - `lib/cmake`
        - `share/aclocal`
        """
        return any(
            DirDetector(dir).detect(store_path)
            for dir in (
                Path("include"),
                Path("lib", "pkgconfig"),
                Path("share", "pkgconfig"),
                Path("lib", "cmake"),
                Path("share", "aclocal"),
            )
        )

    @staticmethod
    def check_doc(store_path: Path) -> bool:
        """
        A `doc` output requires that we have at least one of the following non-empty directories:

        - `share/info`
        - `share/doc`
        - `share/gtk-doc`
        - `share/devhelp`
        - `share/man`
        """
        return any(
            DirDetector(Path("share") / dir).detect(store_path) for dir in ("info", "doc", "gtk-doc", "devhelp", "man")
        )

    @staticmethod
    def check_lib(store_path: Path) -> bool:
        """
        A `lib` output requires that we have a non-empty lib directory containing at least one shared library.
        """
        return DynamicLibraryDetector().detect(store_path)

    @staticmethod
    def check_static(store_path: Path) -> bool:
        """
        A `static` output requires that we have a non-empty lib directory containing at least one static library.
        """
        return StaticLibraryDetector().detect(store_path)

    @staticmethod
    def check_stubs(store_path: Path) -> bool:
        """
        A `stubs` output requires that we have a non-empty `lib/stubs` or `stubs` directory containing at least one
        shared or static library.
        """
        return StubsDetector().detect(store_path)

    @staticmethod
    def check_python(store_path: Path) -> bool:
        """
        A `python` output requires that we have a non-empty `python` directory.
        """
        return DirDetector(Path("python")).detect(store_path)

    @staticmethod
    def check_sample(store_path: Path) -> bool:
        """
        A `sample` output requires that we have a non-empty `samples` directory.
        """
        return DirDetector(Path("samples")).detect(store_path)
