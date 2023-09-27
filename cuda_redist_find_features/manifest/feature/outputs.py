from pathlib import Path

from pydantic import BaseModel, Field
from typing_extensions import Self

from .detectors import DirDetector, DynamicLibraryDetector, ExecutableDetector, StaticLibraryDetector


class FeatureOutputs(BaseModel):
    """
    Describes the different outputs a release can have.

    A number of these checks are taken from
    https://github.com/NixOS/nixpkgs/blob/d4d822f526f1f72a450da88bf35abe132181170f/pkgs/build-support/setup-hooks/multiple-outputs.sh.
    """

    has_bin: bool = Field(False, alias="hasBin")
    has_dev: bool = Field(False, alias="hasDev")
    has_doc: bool = Field(False, alias="hasDoc")
    has_lib: bool = Field(False, alias="hasLib")
    has_static: bool = Field(False, alias="hasStatic")
    has_sample: bool = Field(False, alias="hasSample")

    @classmethod
    def of(cls, store_path: Path) -> Self:
        return cls(
            hasBin=cls.check_has_bin(store_path),
            hasDev=cls.check_has_dev(store_path),
            hasDoc=cls.check_has_doc(store_path),
            hasLib=cls.check_has_lib(store_path),
            hasStatic=cls.check_has_static(store_path),
            hasSample=cls.check_has_sample(store_path),
        )

    @staticmethod
    def check_has_bin(store_path: Path) -> bool:
        """
        A `bin` output requires that we have a non-empty `bin` directory containing at least one file with the
        executable bit set.
        """
        return ExecutableDetector().detect(store_path)

    @staticmethod
    def check_has_dev(store_path: Path) -> bool:
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
    def check_has_doc(store_path: Path) -> bool:
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
    def check_has_lib(store_path: Path) -> bool:
        """
        A `lib` output requires that we have a non-empty lib directory containing at least one shared library.
        """
        return DynamicLibraryDetector().detect(store_path)

    @staticmethod
    def check_has_static(store_path: Path) -> bool:
        """
        A `static` output requires that we have a non-empty lib directory containing at least one static library.
        """
        return StaticLibraryDetector().detect(store_path)

    @staticmethod
    def check_has_sample(store_path: Path) -> bool:
        """
        A `sample` output requires that we have a non-empty `samples` directory.
        """
        return DirDetector(Path("samples")).detect(store_path)
