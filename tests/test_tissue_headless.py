"""The complete tissue example works in a fresh process without initializing desktop modules."""

import json
import shutil
import subprocess
import sys
from pathlib import Path


def test_tissue_example_remains_qt_and_blender_free(tmp_path):
    examples = Path(__file__).resolve().parents[1] / "examples"
    shutil.copytree(examples, tmp_path / "examples")
    code = (
        "import sys; from anthroforge.cli import main; "
        "main(['run', 'examples/tissues.json']); "
        "assert not any(n.startswith(('PySide6','shiboken6','bpy','bmesh')) for n in sys.modules)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=tmp_path, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert all(json.loads(line)["ok"] for line in result.stdout.splitlines())
    assert (tmp_path / "tissues.anthroforge").is_file()
