"""Stacking witnesses are presentation of read-only accepted-state queries."""

from anthroforge.application import tissue_inspection as inspection


def status(tool):
    value = inspection.status(tool.controller.session, "stacking")
    return value if value.get("target") == tool.target else dict(state="idle")


def report(tool):
    state = tool.stacking_status
    return state["report"] if state["state"] == "ready" else {}


def summary(tool):
    state = tool.stacking_status
    report = {key: value for key, value in state.get("report", {}).items() if key != "lines"}
    return dict(state, report=report)


def show(tool, other, side, other_side):
    tool.set_view("intrinsic", "", "Overlay")
    inspection.start(
        tool.controller.session,
        "stacking",
        tool.target,
        other=other,
        side=side,
        other_side=other_side,
    )
    tool.synchronize()


def rows(tool):
    from . import tissue_inspection_scene as scene

    evidence = report(tool)
    if not evidence or tool.stage != "intrinsic":
        return [], []
    other = next(key for key in evidence["names"] if key != tool.target)
    stage = evidence.get("stages", {}).get(other, "intrinsic")
    values, resources = scene.stage_rows(tool, stage, True, other)
    for row in values:
        row["related"] = True
        row["color"] = "#68bacf" if other == evidence["order"]["underlying"] else "#e9ae6e"
        place(tool, row, evidence)
    return values, resources


def lines(tool):
    evidence = report(tool)
    active = {r["owner"]: r for r in tool.model.active_rows()}
    if tool.stage != "intrinsic" or not evidence:
        return []
    for owner, asset in evidence["assets"].items():
        row = active.get(owner)
        if not row or row["geometry_asset"] != asset:
            return []
    return evidence.get("lines", [])


def decorate(tool, values):
    evidence = report(tool)
    if evidence and tool.stage == "intrinsic":
        for row in values:
            if not row["reference"]:
                provider = row["owner"] == evidence["order"]["underlying"]
                row["color"] = "#68bacf" if provider else "#e9ae6e"
                place(tool, row, evidence)


def place(tool, row, evidence):
    from . import tissue_inspection_scene as scene

    row.update(scene.placement(tool.controller.session, evidence["frames"][row["owner"]]))
    row["content"] = scene.content(row, row["mesh_handle"])
