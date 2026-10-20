"""Qualify adaptive exact surfaces using only the packaged CLI and saved project."""

import io
import json
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from check_portable import invoke
from construction_portable import request


def inspect(executable, folder, name):
    return json.loads(invoke(executable, folder, "--cli", "inspect", name))


def captures(state):
    return {
        row["state"]["id"]: {
            name: row["state"][name]
            for name in ("bindings", "binding", "attachment_asset")
            if name in row["state"]
        }
        for row in state["objects"]
        if row["kind"] in ("fiber", "anchor")
    }


def commands(obstacle):
    rows = [request("open", path="input.anthroforge"), request("wait")]
    for name, z in (("restored", 3), ("blocked", 0)):
        rows.extend(
            [
                request("scp.transform", entity=obstacle, values=[0, 0, z, 0, 0, 0, 1, 1, 1]),
                request("wait"),
                request("save", path=name + ".anthroforge", blocked_policy="wait"),
            ]
        )
    return rows


def saved_counts(path, state):
    rows = [o["state"] for o in state["objects"]]
    surface = next(o for o in rows if o.get("exact") is True)
    fibers = [o for o in rows if o.get("bindings") and o["bindings"][0]["role"] == "SCP_GEOMETRY"]
    with ZipFile(path) as archive:
        count = len(read_array(archive, f"assets/{surface['result']['asset']}/vertices.npy"))
        samples = [
            len(read_array(archive, f"paths/{f['result']['asset']}/samples.npy")) for f in fibers
        ]
    return dict(surface_vertices=count, routed_samples=samples)


def read_array(archive, name):
    return np.load(io.BytesIO(archive.read(name)), allow_pickle=False)


def verify(executable, folder, initial):
    evidence = []
    for name, vertices, samples in (("restored", 9, 3), ("blocked", 18, 4)):
        state = inspect(executable, folder, name + ".anthroforge")
        assert captures(state) == captures(initial)
        for row in state["objects"]:
            assert row["state"]["result"]["status"] == "ready", row
        counts = saved_counts(folder / (name + ".anthroforge"), state)
        assert counts == dict(surface_vertices=vertices, routed_samples=[samples, samples]), counts
        evidence.append(dict(phase=name, **counts))
    return evidence


def run(executable, project, folder):
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy2(project, folder / "input.anthroforge")
    initial = inspect(executable, folder, "input.anthroforge")
    obstacle = next(e["id"] for e in initial["entities"] if e["matrix"][3:12:4] == [0, 0, 0])
    (folder / "requests.json").write_text(json.dumps(commands(obstacle)))
    replies = invoke(executable, folder, "--cli", "run", "requests.json")
    assert all(json.loads(line)["ok"] for line in replies.splitlines()), replies
    evidence = verify(executable, folder, initial)
    (folder / "acceptance.json").write_text(json.dumps(evidence, indent=2))
    print(json.dumps(evidence))


if __name__ == "__main__":
    run(*(Path(value).resolve() for value in sys.argv[1:]))
