"""Create the corresponding application source archive without SDKs or local outputs."""

import argparse
import zipfile
from pathlib import Path

from boolean_dependencies import archive_headers

from anthroforge import __version__

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = ("src", "native", "tests", "tools", "docs", "examples", "licenses", ".github", ".vscode")


def sources():
    for path in ROOT.iterdir():
        if path.name == "__init__.py" or path.name.endswith(".anthroforge.lock"):
            continue
        if path.is_file() and path.suffix in (".md", ".toml", ".lock", ".json", ".txt", ".py"):
            yield path
        elif path.is_file() and (path.name.startswith(".") or path.name == "LICENSE"):
            yield path
    for folder in FOLDERS:
        for path in (ROOT / folder).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                yield path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / f"dist/AnthroForge-{__version__}-source.zip"
    )
    target = parser.parse_args().output
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sources():
            archive.write(path, "anthroforge/" + path.relative_to(ROOT).as_posix())
        archive_headers(archive)
    print(target)


if __name__ == "__main__":
    main()
