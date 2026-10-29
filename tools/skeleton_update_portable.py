"""Isolated skeleton preparation and one-action adoption through the relocated executable."""

import hashlib
import json

from assembly_portable import request


def skeleton_update(executable, cwd, invoke):
    path = cwd / "assembly.anthroforge"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    before = json.loads(invoke(executable, cwd, "--cli", "inspect", str(path)))
    root = next(e["id"] for e in before["entities"] if not e["parent"])
    run(executable, cwd, invoke, "skeleton-source", source(root))
    run(executable, cwd, invoke, "skeleton-update", update(root))
    result = json.loads(invoke(executable, cwd, "--cli", "inspect", "skeleton-updated.anthroforge"))
    assert result["entity_count"] == before["entity_count"]
    assert next(e for e in result["entities"] if e["id"] == root)["matrix"][3] == 0.5
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    render(executable, cwd, invoke, result)


def render(executable, cwd, invoke, result):
    invoke(
        executable,
        cwd,
        "--cli",
        "render",
        "skeleton-updated.anthroforge",
        "skeleton-updated.png",
        "--revision",
        str(result["revision"]),
    )


def run(executable, cwd, invoke, name, commands):
    path = cwd / (name + ".json")
    path.write_text(json.dumps(commands), "utf-8")
    result = invoke(executable, cwd, "--cli", "run", str(path))
    assert all(json.loads(line)["ok"] for line in result.splitlines()), result


def source(root):
    return [
        request("open", path="assembly.anthroforge"),
        request("wait"),
        request("scp.transform", entity=root, values=[0.5, 0, 0, 0, 0, 0, 1, 1, 1]),
        request("wait"),
        request("save", path="skeleton-source.anthroforge", blocked_policy="wait"),
    ]


def update(root):
    return [
        request("open", path="assembly.anthroforge"),
        request("wait"),
        request("skeleton_update.inspect", "source", path="skeleton-source.anthroforge"),
        request("skeleton_update.status", wait=True),
        request(
            "skeleton_update.prepare", "candidate", source="$source.source", matches={root: root}
        ),
        request("skeleton_update.status", wait=True),
        request("skeleton_update.apply", token="$candidate.token"),
        request("undo"),
        request("redo"),
        request("save", path="skeleton-updated.anthroforge", blocked_policy="wait"),
    ]
