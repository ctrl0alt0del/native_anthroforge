"""Read-only production graph assembly, exact payload checks and matched shortcut experiments."""

import hashlib
import json
import sys
from contextlib import ExitStack, closing
from pathlib import Path
from time import perf_counter

import numpy as np

from anthroforge.application import projects, storage
from anthroforge.application.object_frames import Frames
from anthroforge.application.session import Session
from anthroforge.core import graph_records
from anthroforge.core.construction import Curve
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import components
from anthroforge.native.scene import entity_frame

OUTPUT = Path("build/assembly-042/production")


def report(name, value):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / (name + ".json")).write_text(json.dumps(value, indent=2), "utf-8")
    print(name, json.dumps(value)[:1600], flush=True)


def inspect(session, path):
    started = perf_counter()
    session.command("assembly.inspect", path=str(path))
    session.wait(180)
    state = session.command("assembly.status")
    assert state["source_state"] == "ready", state["source_error"]
    return state["source"], perf_counter() - started


def copy_selection(session, path, selected, mappings, name):
    token, inspected = inspect(session, path)
    prepared, seconds = prepare_selection(session, token, selected, mappings)
    started = perf_counter()
    result = session.command("assembly.import", token=prepared)
    session.wait(300)
    timings = dict(inspect_s=inspected, prepare_s=seconds, import_s=perf_counter() - started)
    report(name, dict(timings, identities=len(result["identities"]), jobs=result["jobs"]))
    return result["identities"]


def prepare_selection(session, token, selected, mappings):
    started = perf_counter()
    prepared = session.command(
        "assembly.prepare", source=token, selected=selected, mappings=mappings
    )
    session.wait(300)
    state = session.command("assembly.status")
    assert state.get("ready"), state
    return prepared["token"], perf_counter() - started


def assemble(source, destination, path):
    roots = [e.id for e in source.document.entities if not e.parent]
    frames = ("SCP_8:driver-frame", "SCP_9:driver-frame", "SCP_12:driver-frame")
    choices = {
        key: dict(action="include") for key in frames if key in source.document.registry.records
    }
    identities = copy_selection(destination, path, roots, choices, "skeleton")
    choices = {
        key: dict(action="map", target=value)
        for key, value in identities.items()
        if value in destination.document.registry.records
    }
    tissues = [v.id for v in source.document.objects if isinstance(v, TissueVCP)]
    copied = copy_selection(destination, path, tissues, choices, "tissues")
    return identities | copied


def arrays(session, item, frames):
    world = entity_frame(session.engine, item) if isinstance(item, SCP) else frames.world(item.id)
    result = dict(frame=np.asarray(world))
    if isinstance(item, Curve) and item.result.asset:
        path = session.resources.paths[item.result.asset].path
        result["path"] = components.transformed(session.engine, path.array()[:, :3], world)
    else:
        for field in ("result", "base_result", "rest_result", "intrinsic_result", "final_result"):
            key = getattr(getattr(item, field, None), "asset", "")
            if key:
                mesh = session.resources.meshes[key].mesh
                result[field] = components.transformed(session.engine, mesh.array(0), world)
                result[field + "_triangles"] = oriented_triangles(mesh.array(3))
    return result


def oriented_triangles(triangles):
    """Compare oriented connectivity without treating cyclic face order as geometry."""
    shifted = np.take_along_axis(
        triangles, (np.arange(3) + triangles.argmin(axis=1)[:, None]) % 3, axis=1
    )
    return shifted[np.lexsort(shifted.T[::-1])]


def normalized_bindings(item, identities, resources):
    assets = {
        key: "" for group in resources.__dataclass_fields__ for key in getattr(resources, group)
    }
    if isinstance(item, Fiber):
        return graph_records.rewritten(item.bindings, identities, assets)
    if isinstance(item, SCP):
        return graph_records.rewritten(item.attachment, identities, assets)
    return None


def compare_item(source, destination, old, new, frames, identities):
    left, right = arrays(source, old, frames[0]), arrays(destination, new, frames[1])
    errors = {}
    for key in left:
        a, b = left[key], right.get(key, np.empty(0))
        if a.shape != b.shape:
            errors[key] = dict(source=list(a.shape), imported=list(b.shape))
        elif a.size and not np.allclose(a, b, rtol=0, atol=1e-8):
            errors[key] = float(np.max(np.abs(a - b)))
    expected = normalized_bindings(old, identities, source.resources)
    if expected != normalized_bindings(new, {}, destination.resources):
        errors["bindings"] = "Retained binding records differ"
    return errors


def compare(source, destination, identities, name):
    frames = tuple(Frames(s.engine, s.document) for s in (source, destination))
    differences, checked = {}, 0
    for old_id, new_id in identities.items():
        old = source.document.registry.records.get(old_id)
        if not isinstance(old, (SCP, TissueVCP, Curve)):
            continue
        target = destination.document.object(new_id)
        found = compare_item(source, destination, old, target, frames, identities)
        if found:
            differences[old_id] = dict(name=old.name, differences=found)
        checked += 1
    return comparison_report(name, checked, differences, destination.scheduler.errors)


def comparison_report(name, checked, differences, errors):
    value = dict(checked=checked, differences=differences, errors=errors)
    report(name, value)
    return value


def edit(session, case, identities):
    started = perf_counter()
    apply_edit(session, case["mapping"], identities, case["value"])
    session.wait(600)
    return perf_counter() - started


def apply_edit(session, mapping, identities, value):
    if "driver" in mapping:
        session.command(
            "driver.value",
            driver=identities.get(mapping["driver"], mapping["driver"]),
            value=value,
        )
    else:
        ref = dict(mapping["reference"])
        ref["target"] = identities.get(ref["target"], ref["target"])
        session.command("shortcut.set", reference=ref, value=value)


def shortcut_trials(source, destination, identities, plan):
    for case in json.loads(plan.read_text("utf-8"))["cases"]:
        before = destination.document, destination.resources.snapshot()
        original = source.document, source.resources.snapshot()
        times = edit(source, case, {}), edit(destination, case, identities)
        result = compare(source, destination, identities, case["id"])
        if result["differences"]:
            diagnose(source, destination, identities, result["differences"], case["id"])
        report(case["id"] + "-timing", dict(source_s=times[0], imported_s=times[1]))
        projects.adopt(source, *original)
        projects.adopt(destination, *before)
        if result["differences"]:
            raise AssertionError("Shortcut response differs: " + case["id"])


def diagnose(source, destination, identities, failures, name):
    rows = {}
    for key in failures:
        if isinstance(source.document.object(key), Fiber):
            rows[key] = [
                fresh_path(session, target)
                for session, target in ((source, key), (destination, identities[key]))
            ]
    report(name + "-fresh", rows)


def fresh_path(session, key):
    from anthroforge.application import curve_evaluation

    item = session.document.object(key)
    fresh = curve_evaluation.evaluate(session.engine, session.document, session.resources, key, 0)
    accepted = session.resources.paths[item.result.asset].path.array()
    return dict(
        accepted=hashlib.sha256(accepted.tobytes()).hexdigest(),
        fresh=hashlib.sha256(fresh.asset.path.array().tobytes()).hexdigest(),
        delta=float(np.max(np.abs(accepted - fresh.asset.path.array()))),
        status=item.result.status,
        revision=item.result.revision,
        mode=item.update_mode,
        document_mode=session.document.update_mode,
    )


def run(path, plan):
    with ExitStack() as stack:
        source, destination = [stack.enter_context(closing(Session())) for _ in range(2)]
        initial_hash = digest(path)
        projects.adopt(source, *storage.read_package(path, source.engine))
        destination.command("profile.start", seconds=600, memory_mib=256)
        try:
            qualify(source, destination, path, plan)
        finally:
            destination.command(
                "profile.stop", path=str((OUTPUT / "assembly.afprofile.zip").resolve()), wait=True
            )
        assert digest(path) == initial_hash
        report("source-integrity", dict(sha256=initial_hash, unchanged=True))


def qualify(source, destination, path, plan):
    identities = assemble(source, destination, path)
    baseline = compare(source, destination, identities, "baseline")
    storage.atomic_save(
        OUTPUT / "assembly.anthroforge", destination.document, destination.resources
    )
    assert not baseline["differences"], "Imported baseline differs"
    shortcut_trials(source, destination, identities, plan)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


if __name__ == "__main__":
    run(Path(sys.argv[1]), Path(sys.argv[2]))
