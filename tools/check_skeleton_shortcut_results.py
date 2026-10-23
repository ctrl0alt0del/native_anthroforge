"""Compare every accepted surface, path and binding after alternative control mappings."""

import sys
from pathlib import Path

from check_skeleton_shortcut_preservation import Comparison

from anthroforge.application.storage import read_package
from anthroforge.native.mesh import GeometryEngine


def compare(source, candidate):
    engine = GeometryEngine()
    before, resources = read_package(source, engine)
    after, current = read_package(candidate, engine)
    check = Comparison(resources, current)
    for key, item in before.registry.records.items():
        changed = after.object(key)
        if hasattr(item, "matrix"):
            check.value(item.matrix, changed.matrix, key + "/matrix")
        if hasattr(item, "result"):
            from dataclasses import asdict

            check.value(asdict(item.result), asdict(changed.result), key + "/result")
    print(dict(resources=len(check.resources), **check.maxima))


if __name__ == "__main__":
    compare(*(Path(value) for value in sys.argv[1:3]))
