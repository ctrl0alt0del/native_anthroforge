"""Issue operations and the actual Issues panel in a relocated executable."""

import json


def issues(executable, cwd, invoke):
    output = invoke(executable, cwd, "--cli", "run", "examples/issues.json")
    records = [json.loads(line) for line in output.splitlines() if line.startswith("{")]
    assert all(row["ok"] for row in records), records
    named = {row["id"]: row["result"] for row in records if row.get("id")}
    assert named["pending"]["total"] == 1
    assert named["repairs"][-1]["state"] == "DONE"
    assert named["final"]["clean"] and not named["final"]["records"]
    panel(executable, cwd, invoke)


def panel(executable, cwd, invoke):
    smoke = invoke(
        executable,
        cwd,
        "--project",
        "issues-pending.anthroforge",
        "--smoke-test",
        "--smoke-panel",
        "issues",
        "--screenshot",
        str(cwd / "issues.png"),
    )
    assert json.loads(smoke)["desktop_smoke"]
