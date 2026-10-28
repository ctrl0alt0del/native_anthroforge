"""Install the pinned Windows remesher without a Blender runtime dependency."""

import hashlib
import io
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from anthroforge.application.quadwild_bundle import location, manifest, verify


def archive():
    with urllib.request.urlopen(manifest()["release"], timeout=60) as response:
        data = response.read(64 * 1024**2 + 1)
    if len(data) > 64 * 1024**2:
        raise ValueError("QuadWild archive exceeds the download budget.")
    return zipfile.ZipFile(io.BytesIO(data))


def member(bundle, name):
    matches = [p for p in bundle.namelist() if p == name or p.endswith("/" + name)]
    if len(matches) != 1 or bundle.getinfo(matches[0]).file_size > 16 * 1024**2:
        raise ValueError(f"Missing, ambiguous or oversized QuadWild asset: {name}")
    return bundle.read(matches[0])


def install_files(folder, source):
    with archive() if source is None else source_context(source) as reader:
        for name, digest in manifest()["files"].items():
            data = member(reader, name) if source is None else (reader / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError(f"QuadWild fingerprint mismatch: {name}")
            target = folder / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)


def source_context(source):
    from contextlib import nullcontext

    return nullcontext(source)


def main():
    target = location()
    if target.exists():
        print(verify(target))
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target.parent, prefix="quadwild-") as temporary:
        staged = Path(temporary) / "bundle"
        source = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
        install_files(staged, source)
        verify(staged)
        shutil.move(str(staged), str(target))
    print(verify(target))


if __name__ == "__main__":
    main()
