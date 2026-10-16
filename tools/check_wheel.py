from pathlib import Path
from zipfile import ZipFile


def main() -> None:
    wheel = max(Path("dist").glob("*.whl"), key=lambda path: path.stat().st_mtime)
    with ZipFile(wheel) as archive:
        names = archive.namelist()
        assert "anthroforge/desktop/qml/Main.qml" in names, "QML resources are missing"
        assert "anthroforge/py.typed" in names, "Typing marker is missing"
        assert not any(name.startswith(("__init__.py", ".tools/", "build/")) for name in names)
    print(f"Python wheel resources verified: {wheel}")


if __name__ == "__main__":
    main()
