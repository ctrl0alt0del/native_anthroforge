"""Schema-4 tissue workflow through the relocated executable, without developer imports."""

import json
from zipfile import ZipFile

from profiler_portable import validate


def tissues(executable, cwd, invoke):
    output = invoke(executable, cwd, "--cli", "run", "examples/tissues.json")
    assert all(json.loads(line)["ok"] for line in output.splitlines())
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "tissues.anthroforge"))
    items = verify(state, cwd)
    profile(executable, cwd, invoke, items["Layer 1"]["id"])
    capture(executable, cwd, invoke, state, items["Layer 2"]["id"])


def verify(state, cwd):
    items = {row["state"]["name"]: row["state"] for row in state["objects"]}
    assert not state["save_blocked"] and not state["skin_available"]
    assert all(item["result"]["status"] == "ready" for item in items.values())
    assert sum(row["kind"] == "tissue" for row in state["objects"]) == 4
    first, second = items["Layer 1"], items["Layer 2"]
    assert second["stack_plan"]["providers"] == [first["id"]]
    ref = items["Anchor on final tissue"]["binding"]["reference"]
    assert ref == dict(target=second["id"], role="TISSUE_FINAL")
    with ZipFile(cwd / "tissues.anthroforge") as archive:
        assert json.loads(archive.read("manifest.json"))["version"] == 4
    return items


def profile(executable, cwd, invoke, target):
    requests = [
        dict(operation="profile.start"),
        dict(
            operation="tissue.inflation", arguments=dict(target=target, changes=dict(amount=0.025))
        ),
        dict(operation="wait"),
        dict(operation="profile.stop", arguments=dict(path="tissues.afprofile.zip", wait=True)),
    ]
    (cwd / "tissue-profile.json").write_text(json.dumps(requests))
    output = invoke(
        executable, cwd, "--cli", "run", "tissue-profile.json", "--project", "tissues.anthroforge"
    )
    assert all(json.loads(line)["ok"] for line in output.splitlines())
    validate(cwd / "tissues.afprofile.zip", False)


def capture(executable, cwd, invoke, state, target):
    view = dict(selected=target, camera=[0, 0, 0.65, -20, 25, 0, 2], orthographic=True)
    (cwd / "tissue-view.json").write_text(json.dumps(view))
    arguments = ("--cli", "render", "tissues.anthroforge", "tissues.png")
    options = ("--revision", str(state["revision"]), "--view", "tissue-view.json")
    invoke(executable, cwd, *arguments, *options)
    metadata = json.loads((cwd / "tissues.png.json").read_text())
    assert metadata["captured"] and not metadata["window_visible"]
    arguments = ("--project", "tissues.anthroforge", "--smoke-test", "--screenshot")
    smoke = invoke(executable, cwd, *arguments, str(cwd / "tissues-ui.png"))
    assert json.loads(smoke)["desktop_smoke"]
