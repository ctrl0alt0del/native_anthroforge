"""Stage a small, reproducible pyside6-deploy application and its native runtime."""

import configparser
import importlib.metadata
import json
import os
import shutil
import sys
from pathlib import Path

import PySide6
from boolean_dependencies import copy_notices

from anthroforge import __version__
from anthroforge.profiling.identity import build_identity

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "build" / "package-input"
DIST = (
    Path(os.environ.get("AF_PACKAGE_OUTPUT", ROOT / "dist" / __version__)).resolve()
    / "AnthroForge.dist"
)
PACKAGES = (
    "numpy",
    "pyinstantmeshes",
    "Pillow",
    "PySide6",
    "PySide6_Essentials",
    "PySide6_Addons",
    "shiboken6",
    "nuitka",
)


def stage():
    STAGE.mkdir(parents=True, exist_ok=True)
    (STAGE / "build.json").write_text(json.dumps(dict(build_identity(), packaged=True)))
    shutil.copy2(ROOT / "launch.py", STAGE / "AnthroForge.py")
    shutil.copytree(
        ROOT / "src/anthroforge",
        STAGE / "anthroforge",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    config = configparser.ConfigParser()
    config.read(Path(PySide6.__file__).parent / "scripts/deploy_lib/default.spec")
    configure(config)
    with (STAGE / "pysidedeploy.spec").open("w") as stream:
        config.write(stream)


def configure(config):
    config["app"].update(
        title="AnthroForge",
        project_dir=str(STAGE),
        input_file=str(STAGE / "AnthroForge.py"),
        exec_directory=str(DIST.parent),
    )
    config["qt"]["qml_files"] = ",".join(
        str(p) for p in (STAGE / "anthroforge/desktop/qml").glob("*.qml")
    )
    config["qt"]["modules"] = "Core,Gui,Quick,Qml,QuickControls2,Quick3D"
    config["nuitka"]["mode"] = "standalone"
    config["nuitka"]["extra_args"] = nuitka_options()


def nuitka_options():
    # PySide uses deploy_main.py when QML options exceed Windows' command limit.
    # Keep the output contract independent of that temporary entry point.
    return (
        "--noinclude-qt-translations --windows-console-mode=attach --mingw64 --jobs=4 "
        "--output-filename=AnthroForge.exe --output-folder-name=AnthroForge "
        "--include-module=PySide6.QtQuick3D --nofollow-import-to=scipy,pytest,matplotlib,IPython "
        "--include-distribution-metadata=numpy --include-distribution-metadata=PySide6 "
        "--assume-yes-for-downloads --report=compilation-report.xml"
        f" --product-name=AnthroForge --product-version={__version__} --file-version={__version__}"
    )


def finish():
    if not (DIST / "AnthroForge.exe").is_file():
        raise RuntimeError("Deployment did not produce AnthroForge.exe.")
    copy_runtime(DIST / "anthroforge/_runtime")
    shutil.copytree(
        ROOT / "src/anthroforge/desktop/qml", DIST / "anthroforge/desktop/qml", dirs_exist_ok=True
    )
    shutil.copytree(ROOT / "examples", DIST / "examples", dirs_exist_ok=True)
    copy_documentation()
    copy_qt_notices()
    licenses()
    print(DIST / "AnthroForge.exe")


def copy_documentation():
    shutil.copytree(ROOT / "docs", DIST / "docs", dirs_exist_ok=True)
    for name in (
        "README.md",
        "standalone_application_recommendations.md",
        "standalone_technology_stack_analysis.md",
    ):
        shutil.copy2(ROOT / name, DIST / name)


def copy_runtime(runtime):
    copy_topology_runtime(runtime)
    (runtime / "bin").mkdir(parents=True, exist_ok=True)
    shutil.copy2(STAGE / "build.json", runtime / "build.json")
    for name in ("af_native.dll", "af_viewport.dll", "af_profiler.dll"):
        shutil.copy2(ROOT / "build/dev/bin" / name, runtime / "bin" / name)
    shutil.copytree(
        ROOT / "build/dev/qml",
        runtime / "qml",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("*.pdb", "*.lib", "*.exp"),
    )


def licenses():
    target = DIST / "licenses"
    target.mkdir(exist_ok=True)
    for source in [ROOT / "LICENSE", *(ROOT / "native/vendor").glob("*LICENSE*")]:
        shutil.copy2(source, target / source.name)
    shutil.copy2(ROOT / "native/vendor/MPL-2.0.txt", target / "MPL-2.0.txt")
    shutil.copytree(ROOT / "licenses", target, dirs_exist_ok=True)
    copy_native_provenance(target)
    copy_notices(target)
    shutil.copy2(Path(sys.base_prefix) / "LICENSE.txt", target / "CPython-LICENSE.txt")
    for package in PACKAGES:
        package_notices(package, target)


def copy_native_provenance(target):
    copy_relative(ROOT / "native/boolean/PROVENANCE.md", ROOT, DIST)
    for path in (ROOT / "native/migration").rglob("*"):
        if path.is_file() and path.suffix in (".md", ".json"):
            copy_relative(path, ROOT, DIST)
    for name in ("PROVENANCE.md", "numpy_random/PROVENANCE.md", "numpy_random/LICENSE.txt"):
        copy_relative(ROOT / "native/vendor" / name, ROOT, DIST)
    shutil.copy2(ROOT / "native/vendor/numpy_random/LICENSE.txt", target / "NumPy-random.txt")


def copy_relative(path, source_root, target_root):
    destination = target_root / path.relative_to(source_root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)


def copy_qt_notices():
    sdk = Path(os.environ.get("AF_QT_SDK", ROOT / ".tools/qt/6.12.0/msvc2022_64"))
    if (sdk / "sbom").is_dir():
        shutil.copytree(sdk / "sbom", DIST / "licenses/qt-sbom", dirs_exist_ok=True)


def package_notices(package, target):
    distribution = importlib.metadata.distribution(package)
    for relative in distribution.files or ():
        if "license" not in str(relative).lower():
            continue
        source = Path(distribution.locate_file(relative))
        if source.is_file():
            filename = str(relative).replace("/", "_").replace("\\", "_")
            shutil.copy2(source, target / filename)


def copy_topology_runtime(runtime):
    from anthroforge.application.quadwild_bundle import verify

    shutil.copytree(verify(), runtime / "quadwild", dirs_exist_ok=True)
    shutil.copytree(ROOT / "src/anthroforge/data", runtime.parent / "data", dirs_exist_ok=True)


if __name__ == "__main__":
    (finish if "--finish" in sys.argv else stage)()
