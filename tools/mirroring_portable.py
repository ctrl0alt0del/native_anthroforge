"""Exercise strict instance references, frozen measurements and rendering after relocation."""

import json
from zipfile import ZipFile

from anthroforge.application.storage import VERSION


def mirroring(executable, cwd, invoke):
    result = invoke(executable, cwd, "--cli", "run", "examples/mirroring.json")
    rows = [json.loads(line) for line in result.splitlines()]
    assert all(row["ok"] for row in rows), rows
    instance = next(row["result"] for row in rows if row["id"] == "instances")[0]
    assert any(isinstance(row["result"], dict) and row["result"].get("readonly") for row in rows)
    inspect_saved(cwd)
    measurements(executable, cwd, invoke, instance)
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "mirroring.anthroforge"))
    render(executable, cwd, invoke, state["revision"])


def render(executable, cwd, invoke, revision):
    arguments = ("--cli", "render", "mirroring.anthroforge", "mirroring.png")
    invoke(executable, cwd, *arguments, "--revision", str(revision))
    capture = json.loads((cwd / "mirroring.png.json").read_text())
    assert capture["captured"] and not capture["window_visible"]
    assert capture["scene"]["vertices"] >= 72, capture


def inspect_saved(cwd):
    with ZipFile(cwd / "mirroring.anthroforge") as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["version"] == VERSION
        document = manifest["document"]
        assert document["mirror_rules"][0]["enabled"]
        assert document["mirror_accepted"] and document["shared_mirror_targets"]
        assert any(o["state"].get("symmetric") for o in document["objects"])
        assert not any("mirror/" in name for name in archive.namelist())


def measurements(executable, cwd, invoke, instance):
    request = dict(
        operation="measurement.point",
        arguments=dict(entity=instance["id"], triangle=0, weights=[0.2, 0.3, 0.5]),
    )
    (cwd / "mirror-measurement.json").write_text(json.dumps([request]))
    command = ("--cli", "run", "mirror-measurement.json")
    output = invoke(executable, cwd, *command, "--project", "mirroring.anthroforge")
    result = json.loads(output.splitlines()[-1])
    assert result["ok"] and result["result"]["entity"] == instance["id"], result
    assert result["result"]["role"] == "SCP_GEOMETRY"
