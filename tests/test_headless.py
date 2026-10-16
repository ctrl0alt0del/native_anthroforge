import json
import subprocess
import sys


def test_headless_core_does_not_import_qt_or_blender():
    code = "from anthroforge.cli import main; import sys; main(['new']); "
    code += "assert not any(n.startswith(('PySide6', 'bpy', 'bmesh')) for n in sys.modules)"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["entity_count"] == 0


def test_cli_has_native_runtime():
    command = [sys.executable, "-m", "anthroforge", "doctor", "--require-native"]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["native"]["abi"] == 1


def test_cli_rejects_invalid_document():
    command = [sys.executable, "-m", "anthroforge", "new", "--name", " "]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 1
    assert "error" in json.loads(result.stdout)
