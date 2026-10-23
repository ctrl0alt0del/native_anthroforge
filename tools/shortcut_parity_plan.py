"""Freeze donor identities and selected construction for the four-control comparison."""

import copy
import json
import sys
from pathlib import Path

import numpy as np


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2), encoding="utf-8")


def surface_closure(package, keys):
    graphs = package["branching"]["surfaces"]
    result = set(keys)
    for key in keys:
        graph = graphs.get(key)
        if graph:
            result.update([graph["main"], *(b["props"]["surface_id"] for b in graph["branches"])])
    return result


def selected_package(package, units):
    data = copy.deepcopy(package)
    surfaces = surface_closure(data, [u["surface"] for u in units])
    muscles = {u["muscle"] for u in units}
    for key in surfaces:
        graph = data["branching"]["surfaces"].get(key, {})
        muscles.update(b["settings"]["id"] for b in graph.get("branches", ()))
    data["muscles"] = [m for m in data["muscles"] if m["source_id"] in muscles]
    data["fiber_surfaces"] = [s for s in data["fiber_surfaces"] if s["source_id"] in surfaces]
    fibers = {f for s in data["fiber_surfaces"] for f in s["fiber_ids"]}
    data["fibers"] = [f for f in data["fibers"] if f["source_id"] in fibers]
    filter_graph(data, fibers, surfaces)
    for name in ("blobs", "soft_tissues", "shortcuts"):
        data[name] = []
    return data


def filter_graph(data, fibers, surfaces):
    graph = data["branching"]
    graph["fibers"] = {k: v for k, v in graph["fibers"].items() if k in fibers}
    points = {p for row in graph["fibers"].values() for p in row}
    graph["points"] = [p for p in graph["points"] if p["id"] in points]
    graph["surfaces"] = {k: v for k, v in graph["surfaces"].items() if k in surfaces}
    graph["surface_attachments"] = {
        k: v for k, v in graph["surface_attachments"].items() if k in fibers
    }
    if data.get("relationships"):
        wanted = {m["source_id"] for m in data["muscles"]}
        records = data["relationships"]["records"]
        data["relationships"]["records"] = {
            k: v for k, v in records.items() if all(p[0] in wanted for p in v["pair"])
        }


def groups(run, rows, output):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["unit"]["source"]["sha256"], []).append(row)
    result = []
    for digest, members in grouped.items():
        package = read(run / "capture" / digest[:12] / "package.json")
        package = selected_package(package, [r["unit"] for r in members])
        path = output / (digest[:12] + ".json")
        write(path, package)
        result.append(dict(package=str(path), records=members))
    return result


def cases(mapping, inventory):
    result = []
    for number in (4, 15, 16, 21):
        key = f"SHORTCUT_{number}"
        source = next(s for s in inventory["skeleton"]["shortcuts"] if s["id"] == key)
        baseline = mapping[key]["value"]
        value = float(np.float32(3.0 if number == 4 else baseline * 1.05))
        result.append(dict(id=key, label=source["name"], value=value, mapping=mapping[key]))
    return result


def main(run, migration, output):
    output.mkdir(parents=True, exist_ok=True)
    rows = read(run / "migration-state.json")["completed"]
    inventory = read(
        Path(__file__).resolve().parents[1] / "docs/research/shortcuts_030/inventory.json"
    )
    selected = cases(read(migration / "compact-mapping.json"), inventory)
    plan = dict(groups=groups(run, rows, output), cases=selected, records=rows)
    plan["standalone"] = str(migration / "skeleton_96_muscles_shortcuts_v001.anthroforge")
    write(output / "plan.json", plan)
    print(json.dumps(dict(groups=len(plan["groups"]), muscles=len(rows), cases=selected)))


if __name__ == "__main__":
    main(*(Path(p) for p in sys.argv[1:]))
