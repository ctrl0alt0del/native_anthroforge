"""Serial counterbalanced centerline/bevel cost comparison on captured accepted Fiber paths."""

import argparse
import json
from pathlib import Path
from time import perf_counter

import numpy as np

from anthroforge.application import skin_capture as application_capture
from anthroforge.application.object_frames import Frames
from anthroforge.application.session import Session
from anthroforge.core import skin_sources
from anthroforge.core.entities import IDENTITY
from anthroforge.core.fibers import Fiber
from anthroforge.native import skin_capture, skin_fields, skin_gaps


def load_paths(session, project):
    session.command("open", path=str(project))
    session.wait()
    fibers = [item for item in session.document.objects if isinstance(item, Fiber)]
    frame = Frames(session.engine, session.document)
    return [
        (session.resources.paths[item.result.asset].path, frame.world(item.id))
        for item in fibers
        if item.result.asset in session.resources.paths
    ]


def capture(engine, sources, mode, bones=()):
    paths, frames = zip(*sources, strict=True)
    if mode == "bevel":
        paths = [skin_capture.fiber_bevel(path, frame, 0.001) for path, frame in sources]
        frames = [IDENTITY] * len(paths)
    geometry = [row.mesh for row in bones] + list(paths)
    transforms = [row.frame for row in bones] + list(frames)
    kinds = [0] * len(bones) + [int(mode == "centerline")] * len(paths)
    policies = [[0.005, 1, 1]] * len(bones) + [[0.005, 1, 0]] * len(paths)
    return skin_capture.capture_sources(engine, geometry, kinds, transforms, policies)


def skeletal_context(session):
    candidates = skin_sources.candidates(session.document)
    return tuple(
        application_capture.surface(session.engine, session.document, session.resources, row)
        for row in candidates
        if row.kind == "SCP"
    )


def timed(session, name, operation, report):
    start = perf_counter()
    output = session.profiler.call("fiber_skin_benchmark", name, operation)
    report[name] = (perf_counter() - start) * 1000
    return output


def prepare(engine, geometry, resolution):
    return skin_fields.prepare(
        engine,
        geometry.vertices,
        geometry.triangles,
        geometry.skeletal,
        np.ones(len(geometry.vertices)),
        resolution=resolution,
        segments=geometry.segments,
    )


def create_scene(engine, geometry):
    return skin_gaps.create(
        engine,
        geometry.vertices,
        geometry.triangles,
        geometry.owners,
        geometry.policies,
        segments=geometry.segments,
        segment_owners=geometry.segment_owners,
    )


def envelope(session, geometry, resolution, report):
    fields = timed(
        session, "fields_ms", lambda: prepare(session.engine, geometry, resolution), report
    )
    scene = timed(session, "scene_ms", lambda: create_scene(session.engine, geometry), report)
    try:
        result = timed(session, "envelope_ms", lambda: scene.envelope(fields), report)
        report["output_vertices"], report["output_triangles"] = (
            result.mesh.counts[0],
            result.mesh.counts[3],
        )
        return result.mesh.array(0).copy(), result.mesh.array(3).copy()
    finally:
        fields.close()
        scene.close()


def trial(session, sources, mode, resolution, bones=()):
    report = dict(
        mode=mode, fibers=len(sources), path_points=sum(path.count for path, _ in sources)
    )
    geometry = timed(
        session, "capture_ms", lambda: capture(session.engine, sources, mode, bones), report
    )
    report["skeletal_contributors"] = len(bones)
    report["input_vertices"], report["input_triangles"] = (
        len(geometry.vertices),
        len(geometry.triangles),
    )
    report["capture_bytes"] = sum(value.nbytes for value in vars(geometry).values())
    output = envelope(session, geometry, resolution, report) if resolution else None
    return report, output


def compare(session, sources, count, resolution, output, bones=()):
    selected, results, surfaces = sources[:count], [], {}
    for iteration, mode in enumerate(
        ("centerline", "bevel", "bevel", "centerline", "centerline", "bevel")
    ):
        row, surface = trial(session, selected, mode, resolution, bones)
        row["iteration"] = iteration
        results.append(row)
        if surface is not None:
            surfaces[mode + "_vertices"], surfaces[mode + "_triangles"] = surface
        print(json.dumps(row), flush=True)
    if surfaces:
        np.savez(output / f"{count}-{resolution}.npz", **surfaces)
    return dict(count=count, resolution=resolution, trials=results)


def recorded(session, sources, options, bones):
    session.command("profile.start")
    rows = [
        trial(session, sources[:4], mode, options.resolution, bones)[0]
        for mode in ("centerline", "bevel")
    ]
    session.command(
        "profile.stop", path=str(options.output / "fiber-thickness.afprofile.zip"), wait=True
    )
    return rows


def run(session, options):
    sources = load_paths(session, options.project)
    bones = skeletal_context(session)
    reports = [
        compare(session, sources, count, 0, options.output) for count in (1, 32, len(sources))
    ]
    reports.append(compare(session, sources, 4, options.resolution, options.output, bones))
    profiled = recorded(session, sources, options, bones)
    payload = dict(
        project=str(options.project), radius_metres=0.001, reports=reports, profiled=profiled
    )
    (options.output / "performance.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--resolution", type=int, default=64)
    options = parser.parse_args()
    options.output.mkdir(parents=True, exist_ok=True)
    session = Session("Skin Fiber cost qualification")
    try:
        run(session, options)
    finally:
        session.close()


if __name__ == "__main__":
    main()
