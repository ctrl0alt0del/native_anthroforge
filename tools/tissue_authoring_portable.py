"""Verify the shipped authoring commands and persistence in the relocated executable."""

import json


def qualify(executable, cwd, invoke, items):
    first, second = items["Layer 1"]["id"], items["Layer 2"]["id"]
    batch = cwd / "tissue-authoring.json"
    batch.write_text(json.dumps(requests(first, second)), encoding="utf-8")
    output = invoke(executable, cwd, "--cli", "run", batch.name, "--project", "tissues.anthroforge")
    assert all(json.loads(line)["ok"] for line in output.splitlines())
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "tissue-authoring.anthroforge"))
    objects = {row["state"]["id"]: row["state"] for row in state["objects"]}
    assert objects[first]["group"] == objects[second]["group"] == "Family"
    assert not objects[second]["stack_plan"]["providers"]
    verify(objects[first])


def verify(item):
    assert item["stack_settings"]["displacement"] == 0.25
    assert item["parts"][0]["a"] == item["parts"][0]["b"]
    inflation = item["parts"][0]["a"]["inflation"]
    assert inflation["boundary_power"] == 2.5
    assert inflation["profile"]["depths"] == [0.02, 0.04, 0.04, 0.02]
    assert item["result"]["status"] == "ready"


def command(operation, **arguments):
    return dict(operation=operation, arguments=arguments)


def requests(first, second):
    return [
        command("tissue.configure", target=first, changes=dict(group="Family")),
        command("tissue.configure", target=second, changes=dict(group="Family")),
        command("tissue.stacking.configure", target=first, changes=dict(displacement=0.25)),
        command(
            "tissue.inflation",
            target=first,
            changes=dict(mode="SECTION_PROFILE", amount=0.02, boundary_power=2.5),
        ),
        command("tissue.profile.scale", target=first, factor=2),
        command("tissue.side.copy", target=first, source="a", destination="b"),
        command("wait"),
        command("save", path="tissue-authoring.anthroforge", blocked_policy="wait"),
    ]
