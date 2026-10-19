"""Qualify the packaged capture/editor/delivery path without developer dependencies."""

import json
from pathlib import Path
from zipfile import ZipFile

from PySide6.QtGui import QImage


def feedback(executable, cwd, invoke):
    output = cwd / "feedback-probe.json"
    invoke(executable, cwd, "--feedback-probe", str(output))
    result = json.loads(output.read_text())
    assert result["passed"], result
    with ZipFile(Path(result["report"])) as archive:
        report = json.loads(archive.read("report.json"))
        original = QImage.fromData(archive.read("original.png"))
        annotated = QImage.fromData(archive.read("annotated.png"))
    assert report["context"]["build"]["packaged"] and not original.isNull()
    assert original.size() == annotated.size() and original != annotated
    assert [a["kind"] for a in report["annotations"]] == ["rectangle", "arrow", "text"]
    assert original.width() == result["width"] and original.height() == result["height"]
