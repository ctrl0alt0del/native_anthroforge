"""Qualify the relocated app's exclusive modes and separately configured AVBD worker."""

import json
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

from assembly_portable import request
from check_portable import clean_environment


def invoke(executable, cwd, name, commands, runtime="", project=""):
    script = cwd / (name + ".json")
    script.write_text(json.dumps(commands), encoding="utf-8")
    env = clean_environment(True)
    env["ANTHROFORGE_PREFERENCES_PATH"] = str(cwd / "preferences.json")
    if runtime:
        env["ANTHROFORGE_AVBD_RUNTIME"] = str(runtime)
    args = [str(executable), "--cli", "run", str(script)]
    args += ["--project", str(project)] if project else []
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=300)
    (cwd / (name + ".log")).write_text(result.stdout + result.stderr, encoding="utf-8")
    assert result.returncode == 0, result.stdout + result.stderr
    rows = [json.loads(line) for line in result.stdout.splitlines()]
    assert all(row["ok"] for row in rows), rows
    return {row["id"]: row["result"] for row in rows if row.get("id")}


def source(executable):
    cube = str(executable.parent / "examples/primitives/cube.obj")
    return [
        request("import", "bone", path=cube, units=1),
        request("wait"),
        request("skin.inspect", "field"),
        request("skin.configure", section="draft_settings", values=dict(backend="AVBD")),
        request("wait"),
        request("skin.inspect", "avbd"),
        request("skin.status", "status"),
        request("save", path="checkpoint.anthroforgex", blocked_policy="wait"),
    ]


def verify_source(values):
    assert values["field"]["envelope"]["asset"]
    assert values["status"]["pipeline"]["phase"] == "current", values["status"]
    skin = values["avbd"]
    assert skin["applied_draft"]["configuration"]["builder"] == "AVBD"
    assert len(skin["checkpoints"]) == 1 and skin["checkpoints"][0]["durable"]


def unavailable(executable, cwd):
    commands = [
        request("skin.inspect", "before"),
        request("skin.envelope.build"),
        request("wait"),
        request("skin.inspect", "after"),
        request("skin.status", "status"),
    ]
    project = cwd / "checkpoint.anthroforgex"
    values = invoke(executable, cwd, "unavailable", commands, project=project)
    assert values["before"]["envelope"] == values["after"]["envelope"]
    state = values["status"]["pipeline"]
    assert state["phase"] == "failed" and state["can_retry"] and "unavailable" in state["reason"]


def resumed(executable, cwd, runtime):
    commands = [
        request("skin.status", "opened"),
        request("skin.inspect", "before"),
        request("skin.envelope.build"),
        request("wait"),
        request("skin.inspect", "after"),
        request("save", path="ordinary.anthroforge", blocked_policy="wait"),
    ]
    values = invoke(executable, cwd, "resumed", commands, runtime, cwd / "checkpoint.anthroforgex")
    assert values["opened"]["pipeline"]["phase"] == "restored"
    assert values["before"]["checkpoints"] == values["after"]["checkpoints"]
    with ZipFile(cwd / "ordinary.anthroforge") as archive:
        assert not json.loads(archive.read("manifest.json"))["document"]["skin"]["checkpoints"]


def final_requests(bone):
    return [
        request("skin.configure", section="topology_settings", values=dict(backend="INSTANT")),
        request("skin.configure", section="topology_settings", values=dict(target_quads=1000)),
        request("skin.configure", section="deformation_settings", values=dict(proxy_resolution=8)),
        request("skin.update_mode", mode="FINAL"),
        request("wait"),
        request("skin.inspect", "before"),
        request("scp.transform", entity=bone, values=[0.1, 0, 0, 0, 0, 0, 1, 1, 1]),
        request("wait"),
        request("skin.inspect", "after"),
        request("skin.status", "status"),
        request("save", path="final.anthroforgex", blocked_policy="wait"),
    ]


def final_mode(executable, cwd, runtime, bone):
    values = invoke(
        executable, cwd, "final", final_requests(bone), runtime, cwd / "checkpoint.anthroforgex"
    )
    before, after = values["before"], values["after"]
    assert values["status"]["pipeline"]["phase"] == "current", values["status"]
    assert after["update_mode"] == "FINAL" and after["final"]["asset"]
    assert before["final"]["asset"] != after["final"]["asset"]
    for key in ("envelope", "topology", "reference"):
        assert before[key] == after[key], key


def main():
    executable, cwd, runtime = (Path(arg).resolve() for arg in sys.argv[1:4])
    cwd.mkdir(parents=True, exist_ok=True)
    values = invoke(executable, cwd, "source", source(executable), runtime)
    verify_source(values)
    unavailable(executable, cwd)
    resumed(executable, cwd, runtime)
    final_mode(executable, cwd, runtime, values["bone"]["entity_id"])
    report = dict(passed=True, executable=str(executable), external_runtime=str(runtime))
    (cwd / "qualification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
