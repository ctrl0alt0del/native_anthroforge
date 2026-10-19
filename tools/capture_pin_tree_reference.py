"""Capture the accepted addon's analytic pin-exit tree as a portable native fixture."""

import hashlib
import importlib
import json
import sys
from pathlib import Path


def write_tree(path, tree, result):
    rows = [f"{len(tree.points)} {len(result[0])} {result[1]}"]
    rows.extend(
        " ".join(map(repr, (*map(float, p), int(i))))
        for p, i in zip(tree.points, tree.parents, strict=True)
    )
    rows.extend(" ".join(map(repr, map(float, point))) for point in result[0])
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def capture(addon, output):
    sys.path.insert(0, str(addon))
    module = importlib.import_module("tests.unit.test_fiber_pin_recovery")
    tree = module.tree_fixture()
    result = module.drain(
        module.solve_tree(tree, module.PinExitPolicy(directions=128, growth_batches=64))
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    write_tree(output, tree, result)
    files = (addon / "core/vcp/v2/planner_pin_tree.py", Path(module.__file__))
    sources = {str(p.relative_to(addon)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    output.with_suffix(".json").write_text(json.dumps(dict(sources=sources), indent=2) + "\n")


if __name__ == "__main__":
    capture(Path(sys.argv[1]).resolve(), Path(sys.argv[2]))
