"""Position-only skin update against one immutable anatomical reference."""

import json
from typing import Any

from anthroforge.native import construction, skin_contact, skin_deformation, topology

from . import skin_assets, skin_support_capture, worker_memory
from .skin_results import ComputedStage


def reference(document: Any, resources: Any) -> Any:
    value = resources.skin.get(document.skin.reference)
    if value is None:
        raise ValueError("Build a skin deformation reference first.")
    return value


def evaluate(engine: Any, document: Any, resources: Any, cancel: int) -> ComputedStage:
    retained = reference(document, resources)
    arrays = retained.arrays
    targets = skin_support_capture.targets(engine, document, resources, retained, cancel)
    with skin_deformation.Preparation(
        engine, arrays, document.skin.deformation_settings, cancel
    ) as solver:
        proposed, diagnostics, predicted = solver.solve(targets, cancel)
    return finish(engine, document, resources, retained, (proposed, diagnostics, predicted), cancel)


def finish(
    engine: Any, document: Any, resources: Any, retained: Any, solved: Any, cancel: int
) -> ComputedStage:
    arrays = retained.arrays
    current = resources.meshes[document.skin.final.asset].mesh
    base = original(engine, arrays, current, cancel)
    proposed, diagnostics, predicted = solved
    points, contact = skin_contact.evaluate(
        engine, arrays, current.array(0), proposed, worker_memory.budget(), cancel
    )
    mesh = topology.finalize(construction.deformed(base, points, cancel), current, cancel)
    return ComputedStage(mesh, report(retained, diagnostics, predicted, contact))


def report(reference: Any, diagnostics: Any, predicted: Any, contact: Any) -> Any:
    arrays = dict(solver_diagnostics=diagnostics, predicted=predicted, contact=contact)
    return skin_assets.create(arrays, metadata(reference, contact))


def original(engine: Any, arrays: Any, current: Any, cancel: int) -> Any:
    base = topology.restore(
        engine, [arrays[k] for k in ("vertices", "corners", "offsets", "triangles", "polygons")]
    )
    if not topology.same_topology(base, current, cancel):
        raise ValueError("Skin vertex identity/connectivity changed; rebuild its reference.")
    return base


def metadata(reference: Any, contact: Any) -> dict[str, Any]:
    warnings = []
    if contact[0]:
        warnings.append("Skin contact projection retains unresolved contacts.")
    if contact[3]:
        warnings.append("Skin contact projection reached its advisory work limit.")
    return dict(
        kind="final_skin",
        reference=reference.digest,
        warnings=warnings,
        tissue_surface=json.loads(reference.metadata)["tissue_surface"],
        contact_coverage="incomplete",
    )
