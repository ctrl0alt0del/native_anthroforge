import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_python_functions_stay_within_fifteen_lines():
    violations = []
    for folder in ("src", "tools", "tests"):
        for path in (ROOT / folder).rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    length = node.end_lineno - node.lineno + 1
                    if length > 15:
                        violations.append(f"{path.relative_to(ROOT)}:{node.lineno} ({length})")
    assert not violations, "\n".join(violations)


def imports(path):
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            yield node.module or ""


def test_shared_core_has_no_editor_dependency():
    forbidden = ("bpy", "bmesh", "mathutils", "PySide6", "anthroforge.desktop")
    paths = (ROOT / "src" / "anthroforge" / name for name in ("core", "application", "native"))
    violations = [
        f"{path}: {name}"
        for base in paths
        for path in base.rglob("*.py")
        for name in imports(path)
        if name.startswith(forbidden)
    ]
    assert not violations, "\n".join(violations)
