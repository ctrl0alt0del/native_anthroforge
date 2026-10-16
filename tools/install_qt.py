"""Use aqt's verified downloader with Qt 6.12's per-compiler repository layout."""

import sys
from importlib.metadata import version

import aqt
from aqt.metadata import QtRepoProperty


def repository_extension(architecture: str, is_version_ge_6: bool) -> str:
    if architecture != "win64_msvc2022_64" or not is_version_ge_6:
        raise ValueError("This installer is scoped to Qt 6.12.0 Windows MSVC x64.")
    return "msvc2022_64"


ARGUMENTS = [
    "aqt",
    "install-qt",
    "windows",
    "desktop",
    "6.12.0",
    "win64_msvc2022_64",
    "-O",
    ".tools/qt",
    "-m",
    "qtquick3d",
    "qtshadertools",
    "--archives",
    "qtbase",
    "qtdeclarative",
    "qtsvg",
    "qttools",
]


def main() -> int:
    if version("aqtinstall") != "3.3.0":
        raise RuntimeError("Review the Qt repository compatibility shim for this aqt version.")
    QtRepoProperty.extension_for_arch = staticmethod(repository_extension)
    sys.argv = ARGUMENTS
    return aqt.main()


if __name__ == "__main__":
    raise SystemExit(main())
