"""Exercise frozen evidence export through a hidden renderer and a Qt-free caller."""

import json
import os
import sys
from contextlib import closing
from pathlib import Path
from zipfile import ZipFile

from anthroforge.application import report_renderer
from anthroforge.application.session import Session

OUTPUT = Path("build/reconstruction-042/export")


def renderer():
    from anthroforge.cli import main
    from anthroforge.desktop import offscreen, runtime

    path = Path(os.environ["AF_NATIVE_BUILD"]).resolve()
    runtime.build_directory = offscreen.build_directory = lambda: path
    sys.argv.pop(1)
    raise SystemExit(main())


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report_renderer.launcher = lambda: [sys.executable, str(Path(__file__).resolve()), "--render"]
    with closing(Session()) as session:
        key = fixture(session)
        session.command(
            "reconstruction.compare.start",
            subject=key,
            before=dict(stage="final"),
            after=dict(stage="final"),
            plane=[0, 0, 1, 0],
        )
        session.command("reconstruction.compare.status", wait=True)
        export(session)
        assert not any(name.startswith("PySide6") for name in sys.modules)


def fixture(session):
    key = session.command("import", path="examples/primitives/cube.obj", units=0.1)["entity_id"]
    session.wait()
    return key


def export(session):
    path = (OUTPUT / "comparison.afinspection.zip").resolve()
    session.command(
        "reconstruction.compare.export", path=str(path), camera=[0, 0, 0, -18, 25, 0.5], wait=True
    )
    with ZipFile(path) as archive:
        state = json.loads(archive.read("inspection.json"))
        (OUTPUT / "comparison.png").write_bytes(archive.read("image.png"))
    assert state["image"]["captured"] and not state["image"]["window_visible"]
    assert state["view"]["reconstruction"]["report"]["distances"]["material"]["maximum"] == 0
    (OUTPUT / "result.json").write_text(json.dumps(state["image"], indent=2))


if __name__ == "__main__":
    renderer() if "--render" in sys.argv else run()
