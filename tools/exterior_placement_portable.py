"""Exercise Boolean placement and original-material attachment capture in a clean executable."""

import json
from pathlib import Path
from zipfile import ZipFile

from construction_portable import request


def cavity(cwd):
    rows = (cwd / "examples/primitives/cube.obj").read_text().splitlines()
    vertices = [[float(v) for v in row.split()[1:]] for row in rows if row.startswith("v ")]
    faces = [[int(v) for v in row.split()[1:]] for row in rows if row.startswith("f ")]
    output = [
        "v " + " ".join(str(v * scale) for v in row) for scale in (1, 0.5) for row in vertices
    ]
    output += [
        "f " + " ".join(str(v + offset) for v in row[::direction])
        for offset, direction in ((0, 1), (8, -1))
        for row in faces
    ]
    (cwd / "placement-cavity.obj").write_text("\n".join(output) + "\n")


def commands(target="placement-cavity.obj"):
    return [
        dict(id="bone", **request("import", path=target, units=1)),
        request("wait"),
        placed_curve(),
        request("wait"),
        request("fiber.create", curve="$curve"),
        dict(id="point", **request("construction.point.create", position=[0.1, 0, 0])),
        request("anchor.create", source="$point"),
        request("wait"),
        request("save", path="exterior-placement.anthroforge", blocked_policy="wait"),
    ]


def placed_curve():
    projection = dict(
        targets=["$bone.entity_id"], queries=[[x, 0, 0, 0, 0, 1, 0, 1] for x in (-0.1, 0.1)]
    )
    return dict(
        id="curve",
        **request(
            "curve.create",
            projection=projection,
            points=[dict(position=[x, 0, 0.25]) for x in (-0.1, 0.1)],
        ),
    )


def exterior_placement(executable, cwd, invoke):
    cavity(cwd)
    for target in ("placement-cavity.obj", "examples/primitives/cube.obj"):
        qualify_placement(executable, cwd, invoke, target)


def recorded_commands(target):
    return [
        request("profile.start"),
        *commands(target),
        request("profile.stop", path=Path(target).stem + ".afprofile.zip", wait=True),
    ]


def qualify_placement(executable, cwd, invoke, target):
    script = cwd / "exterior-placement.json"
    script.write_text(json.dumps(recorded_commands(target)))
    output = invoke(executable, cwd, "--cli", "run", script.name)
    assert all(json.loads(line)["ok"] for line in output.splitlines()), output
    state = json.loads(
        invoke(executable, cwd, "--cli", "inspect", "exterior-placement.anthroforge")
    )
    verify(state)
    verify_profile(cwd / (Path(target).stem + ".afprofile.zip"))


def verify_profile(path):
    with ZipFile(path) as archive:
        events = json.loads(archive.read("trace.json"))["traceEvents"]
    assert any(e["cat"] == "native" and e["name"] == "af_surface_query" for e in events)
    queries = [e for e in events if e["cat"] == "cache" and e["args"]["cache"] == "surface_query"]
    inserts = [e["args"] for e in queries if e["name"] == "insert"]
    assert inserts and all(0 < e["bytes"] <= e["retained_bytes"] <= e["budget"] for e in inserts)
    assert any(e["name"] == "hit" for e in queries)


def verify(state):
    objects = {row["kind"]: row["state"] for row in state["objects"]}
    curve, fiber, anchor = (objects[k] for k in ("curve", "fiber", "anchor"))
    assert all(0.5 < p["position"][2] < 0.500001 for p in curve["points"])
    records = [b["attachment"]["binding"] for b in fiber["bindings"]]
    records.append(anchor["binding"]["attachment"]["binding"])
    assert all(record and max(record[:3]) < 8 for record in records)
    assert all(item["result"]["status"] == "ready" for item in objects.values())
    assert not state["save_blocked"]
