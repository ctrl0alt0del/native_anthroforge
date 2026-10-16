# Development guide

## Setup and daily use

Requirements: PowerShell, uv, Visual Studio C++/Windows SDK tools and LLVM/clang-cl.
The setup discovers the C++ and LLVM installations independently.

```powershell
./tools/setup.ps1
./tools/check.ps1
./tools/run.ps1
```

Setup installs CPython 3.12.12, the locked desktop/numerical development environment,
the matching Qt 6.12.0 MSVC x64 SDK, and builds native targets. Local Python/Qt SDKs live
under .tools; the virtual environment is .venv. The addon is not a runtime dependency.

The Qt installer has an explicit repository-layout adapter for aqtinstall 3.3.0 and the
Qt 6.12 compiler-specific archive location. It retains aqt checksum verification.
[Qt repository](https://download.qt.io/online/qtsdkrepository/windows_x86/desktop/qt6_6120/),
[aqt docs](https://aqtinstall.readthedocs.io/en/stable/getting_started.html).

| Command | Purpose |
| --- | --- |
| ./tools/build-native.ps1 | Native rebuild and CTest |
| ./tools/check.ps1 | Lock, Ruff, configured mypy, native/style checks, pytest, numerical imports, doctor |
| uv run --no-sync python -m anthroforge run examples/assembly.json | Create and save the example assembly |
| uv run --no-sync python tools/gui_acceptance.py assembly.anthroforge | Real QQuickWindow drag/undo and save/reopen |
| uv run --no-sync python tools/ui_acceptance.py assembly.anthroforge | Text-safe shortcuts, numeric edit/undo, search, sections, resizing and empty-state captures |
| ./tools/smoke-desktop.ps1 | Bounded desktop startup and capture |
| ./tools/build-package.ps1 | Development wheel/source package |
| ./tools/package.ps1 | Portable Windows executable and dependencies |
| uv run --no-sync python tools/source_archive.py | Companion source archive |
| uv run --no-sync python tools/check_portable.py PATH_TO_EXE build/portable-check | Minimal-environment runtime acceptance |

For release tooling, install the packaging group without removing desktop/numerical extras:
`uv sync --locked --all-extras --group qt-sdk --group packaging`.
The deployment uses pyside6-deploy and Nuitka 4.1.1, explicitly selects its supported
downloaded MinGW compiler, and keeps the full standalone directory. A short Nuitka cache
path avoids Windows compiler header path limits. Downloads occur only during build.
Neither packaging command publishes anything.

AF_QT_SDK can point to an existing matching SDK for native build/deployment.
UV_PROJECT_ENVIRONMENT and PYTHONPATH can select an existing environment and another source
checkout. ANTHROFORGE_NATIVE_LIBRARY overrides the numerical native library path.
The packaged app resolves its native libraries beside its own code.

## Reproducible qualification

The normal test suite contains the captured Blender reference matrices, so Blender is
not required to run it. To regenerate them explicitly:

```powershell
blender --background --factory-startup --python tools/capture_addon_parity.py -- ADDON_PATH build/addon-parity.json
uv run --no-sync python tools/check_addon_parity.py build/addon-parity.json
```

The reference script creates a temporary in-memory scene and never saves a .blend.
tools/viewport_benchmark.py accepts an anatomical STL path and creates 32 independent
instances for navigation/picking measurements. Large user assets remain outside source.

All authored functions stay within 15 physical lines. Unchanged third-party headers and
the preserved addon kernel retain upstream formatting. Shared core/application/native
Python code cannot import Blender or Qt. Numerical geometry and optimization loops belong
in C++, with owned batched inputs/results across the boundary.

CMake portable-core builds the numerical engine without Qt. Windows execution is verified;
Linux/macOS runtime paths and the Windows/Linux CI workflow are prepared but not locally
certified. The old root __init__.py is an unrelated Blender stub; preserve it and use the
src package and configured test paths.

The optional addon-check CMake preset still accepts AF_ADDON_SOURCE for the original
smoothing kernel qualification. It reads source in place and writes only build outputs.
Future migrations should add equivalent parity evidence instead of treating the entire
addon as already portable.

Development numerics extras remain installed for future work. They are excluded from
the 0.1 portable runtime because 0.1 does not use them. In particular pytetwild[all]
supplies its required PyVista accessor dependency while Qt remains the application renderer.
