"""Compare original authored records, accepted geometry and retained binding payloads."""

import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

from anthroforge.application.storage import read_package
from anthroforge.native.mesh import GeometryEngine

RUNTIME = {
    "generation",
    "revision",
    "result_generation",
    "pose_receipt",
    "inputs",
    "diagnostics",
    "pending",
}


class Comparison:
    def __init__(self, before, after):
        self.before, self.after = before, after
        self.resources = set()
        self.maxima = dict(authored=0.0, mesh=0.0, path=0.0, path_frames=0.0)

    def array(self, before, after, group, tolerance=1e-8):
        assert before.shape == after.shape, (group, before.shape, after.shape)
        error = float(np.max(np.abs(before - after), initial=0))
        self.maxima[group] = max(self.maxima[group], error)
        assert error <= tolerance, (group, error)

    def resource(self, before, after):
        if (before, after) in self.resources:
            return True
        for kind in ("meshes", "paths", "attachments", "images"):
            originals, candidates = getattr(self.before, kind), getattr(self.after, kind)
            if before not in originals:
                continue
            assert after in candidates, (kind, before, after)
            self.resources.add((before, after))
            getattr(self, kind)(originals[before], candidates[after])
            return True
        return False

    def meshes(self, before, after):
        self.array(before.mesh.array(0), after.mesh.array(0), "mesh")
        for index in range(1, 5):
            assert np.array_equal(before.mesh.array(index), after.mesh.array(index)), (
                self.address,
                index,
            )

    def paths(self, before, after):
        a, b = before.path, after.path
        assert a.closed == b.closed
        self.array(a.array()[:, [0, 1, 2, 9, 10]], b.array()[:, [0, 1, 2, 9, 10]], "path")
        self.array(a.array(1), b.array(1), "path")
        self.array(a.array()[:, 3:9], b.array()[:, 3:9], "path_frames", float("inf"))

    def attachments(self, before, after):
        assert before.targets == after.targets
        for name in ("owners", "weights", "bindings", "records"):
            assert np.array_equal(getattr(before.field, name), getattr(after.field, name)), name
        assert np.array_equal(before.field.path.array(), after.field.path.array())

    def images(self, before, after):
        assert before == after

    def value(self, before, after, address):
        self.address = address
        if isinstance(before, dict):
            self.mapping(before, after, address)
        elif isinstance(before, (tuple, list)):
            assert len(before) == len(after), address
            for index, (a, b) in enumerate(zip(before, after, strict=True)):
                self.value(a, b, f"{address}/{index}")
        elif isinstance(before, str) and self.resource(before, after):
            return
        elif type(before) in (float, int) and type(after) in (float, int):
            self.maxima["authored"] = max(self.maxima["authored"], abs(before - after))
            assert abs(before - after) <= 1e-8, (address, before, after)
        else:
            assert before == after, (address, before, after)

    def mapping(self, before, after, address):
        assert before.keys() == after.keys(), address
        for key, value in before.items():
            if key not in RUNTIME and not key.endswith("_revision"):
                self.value(value, after[key], f"{address}/{key}")


def compare(source, candidate, output):
    engine = GeometryEngine()
    before, resources = read_package(source, engine)
    after, current = read_package(candidate, engine)
    check = Comparison(resources, current)
    assert before.registry.records.keys() == after.registry.records.keys()
    for key, item in before.registry.records.items():
        check.value(asdict(item), asdict(after.object(key)), key)
    for key in ("workspaces", "junctions", "attachments_enabled", "metres_per_unit"):
        assert getattr(before, key) == getattr(after, key), key
    result = dict(
        records=len(before.registry.records), resources=len(check.resources), **check.maxima
    )
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    compare(*(Path(value) for value in sys.argv[1:4]))
