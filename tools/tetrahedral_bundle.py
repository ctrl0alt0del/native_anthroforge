"""Copy the pinned numerical extension and its wheel-owned DLL dependencies."""

import shutil

from anthroforge.native.tetrahedral_extension import extension, location


def copy_runtime(runtime):
    source = location()
    root = runtime / "tetrahedral"
    module = root / "pytetwild"
    module.mkdir(parents=True, exist_ok=True)
    shutil.copy2(extension(source), module)
    libraries = source.parent / "pytetwild.libs"
    if libraries.is_dir():
        shutil.copytree(libraries, root / libraries.name, dirs_exist_ok=True)
