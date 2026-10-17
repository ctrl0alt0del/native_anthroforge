"""Fail explicitly when a read-only cloud base lacks required system dependencies."""

import ctypes
import os
import shutil

LIBRARIES = ("libEGL.so.1", "libGL.so.1", "libOpenGL.so.0", "libxkbcommon.so.0", "libdbus-1.so.3")


def main():
    for command in (os.environ.get("CXX", "c++"), "git", "clang-tidy", "shellcheck"):
        if shutil.which(command) is None:
            raise RuntimeError(f"Cloud base is missing required command: {command}")
    for library in LIBRARIES:
        ctypes.CDLL(library)
    from PySide6 import QtCore, QtGui

    assert QtCore.qVersion() and QtGui.QColor("white").isValid()
    print("Cloud host compiler, runtime libraries and Qt test imports passed.")


if __name__ == "__main__":
    main()
