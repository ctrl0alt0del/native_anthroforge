"""Exercise Boolean placement and original-material attachment capture in a clean executable."""

import json

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


def commands():
    return [
        dict(id="bone", **request("import", path="placement-cavity.obj", units=1)),
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
    script = cwd / "exterior-placement.json"
    script.write_text(json.dumps(commands()))
    output = invoke(executable, cwd, "--cli", "run", script.name)
    assert all(json.loads(line)["ok"] for line in output.splitlines()), output
    state = json.loads(
        invoke(executable, cwd, "--cli", "inspect", "exterior-placement.anthroforge")
    )
    verify(state)


def verify(state):
    objects = {row["kind"]: row["state"] for row in state["objects"]}
    curve, fiber, anchor = (objects[k] for k in ("curve", "fiber", "anchor"))
    assert all(0.5 < p["position"][2] < 0.500001 for p in curve["points"])
    records = [b["attachment"]["binding"] for b in fiber["bindings"]]
    records.append(anchor["binding"]["attachment"]["binding"])
    assert all(record and max(record[:3]) < 8 for record in records)
    assert all(item["result"]["status"] == "ready" for item in objects.values())
    assert not state["save_blocked"]
