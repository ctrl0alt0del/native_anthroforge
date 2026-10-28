"""Measure the unchanged addon's requested gap precision for restored Fiber surfaces."""

import argparse
import json
import sys
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from check_skin_fiber_performance import capture, load_paths, prepare, region

from anthroforge.application import worker_memory
from anthroforge.application.session import Session


def source_queries(geometry, addon):
    sys.path.insert(0, str(addon))
    lib = import_module("core.draft_skin.gap_native").library()
    handle = lib.af_skin_gap_create(
        geometry.vertices,
        len(geometry.vertices),
        geometry.triangles,
        len(geometry.triangles),
        geometry.owners,
        len(geometry.policies),
        geometry.policies,
    )
    if not handle:
        raise ValueError("Addon rejected captured contributors.")
    return SimpleNamespace(lib=lib, handle=handle)


def precision(geometry, fields, addon):
    queries = source_queries(geometry, addon)
    reach = float(np.ptp(geometry.vertices, axis=0).max()) * 3 * 9.51539268851356 / 220
    try:
        width, count = import_module("core.draft_skin.gap_tiles").exterior_precision(
            queries, fields.array(3), fields.origin, fields.voxel, reach
        )
    finally:
        queries.lib.af_skin_gap_destroy(queries.handle)
    return describe_precision(fields.voxel, width, count)


def describe_precision(coarse, width, count):
    fine = min(coarse, width / 5.5) if count else coarse
    return dict(
        coarse_voxel=coarse,
        protected_gap_width=width,
        gap_faces=count,
        fine_voxel=fine,
        linear_refinement=coarse / fine,
    )


def run(session, options):
    load_paths(session, options.project)
    paths, bones = region(session, options)
    geometry = capture(session.engine, paths, "bevel", bones)
    fields = prepare(session.engine, geometry, 220, worker_memory.budget())
    try:
        result = precision(geometry, fields, options.addon)
    finally:
        fields.close()
    options.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("addon", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--fiber-prefix", action="append", default=[])
    options = parser.parse_args()
    session = Session("Skin gap precision qualification")
    try:
        run(session, options)
    finally:
        session.close()


if __name__ == "__main__":
    main()
