"""Analytical parity report; missing outputs and failed updates remain explicit."""

import sys
from pathlib import Path

import numpy as np
from shortcut_parity_metrics import endpoints, response, statistics, surface
from shortcut_parity_plan import read, write

from anthroforge.native.mesh import GeometryEngine


def dataset(folder, runtime, case):
    path = folder / runtime / case
    state = read(path / "state.json")
    state["lookup"] = {r["id"]: r for r in state["objects"]}
    return state, np.load(path / "geometry.npz")


def length_scale(state):
    contract = state.get("unit_contract")
    return contract["meters_per_world_unit"] if contract else state.get("scene_scale", 1.0)


def geometry(data, key):
    state, arrays = data
    return arrays[key + "__vertices"] * length_scale(state), arrays[key + "__triangles"]


def mesh_comparison(engine, key, a, b, initial):
    va, vb = geometry(a, key), geometry(b, key)
    oa, ob = geometry(initial[0], key), geometry(initial[1], key)
    return dict(
        surface_distance=surface(engine, va, vb),
        response=response(oa[0], va[0], ob[0], vb[0]),
        app_vertices=len(va[0]),
        blender_vertices=len(vb[0]),
        centroid_response_error=float(
            np.linalg.norm((va[0].mean(0) - oa[0].mean(0)) - (vb[0].mean(0) - ob[0].mean(0)))
        ),
    )


def path_comparison(key, a, b, initial):
    points = [d[1][key + "__path"] * length_scale(d[0]) for d in (*initial, a, b)]
    oa, ob, va, vb = points
    result = dict(endpoints=endpoints(oa, va, ob, vb), app_samples=len(va), blender_samples=len(vb))
    if va.shape == vb.shape:
        result["indexed_path_distance"] = statistics(np.linalg.norm(va - vb, axis=1))
    if oa.shape == ob.shape == va.shape == vb.shape:
        result["indexed_response_error"] = statistics(np.linalg.norm((va - oa) - (vb - ob), axis=1))
    return result


def compare_object(engine, key, a, b, initial):
    record = a[0]["lookup"][key]
    result = dict(id=key, name=record["name"], kind=record["kind"], mirror=key.endswith("_mirror"))
    suffix = "__path" if record["kind"] == "Fiber" else "__vertices"
    if any(key + suffix not in d[1] for d in (*initial, a, b)):
        return dict(result, unavailable=True, reason="Missing baseline or current geometry")
    metric = (
        path_comparison(key, a, b, initial)
        if suffix == "__path"
        else mesh_comparison(engine, key, a, b, initial)
    )
    return dict(result, **metric)


def compare_case(engine, output, name, initial):
    a, b = dataset(output, "app", name), dataset(output, "blender", name)
    left, right = set(a[0]["lookup"]), set(b[0]["lookup"])
    assert left == right, dict(app_only=sorted(left - right), blender_only=sorted(right - left))
    rows = []
    for key in sorted(left):
        rows.append(compare_object(engine, key, a, b, initial))
        if len(rows) % 30 == 0:
            print(name, len(rows), "/", len(left), flush=True)
    write(output / (name + "-comparison.json"), report(name, rows, a[0], b[0]))


def report(name, rows, app, blender):
    return dict(
        case=name,
        units="metres",
        rows=rows,
        addon_runtime=blender["runtime"],
        app_errors=app["errors"],
    )


def main(output, names):
    engine = GeometryEngine()
    initial = dataset(output, "app", "baseline"), dataset(output, "blender", "baseline")
    for name in names:
        compare_case(engine, output, name, initial)


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2:])
