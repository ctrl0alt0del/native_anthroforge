"""Publish retained advisory evidence; diagnostics never choose or repair geometry."""

import json
from collections.abc import Callable
from typing import Any

from anthroforge.native import skin_final_quality as native

from . import worker_memory

SOLVER = (
    "iterations",
    "residual",
    "minimum_proxy_j",
    "outside_embeddings",
    "maximum_outside_normalized",
    "replay_error",
)
CONTACT = (
    "unresolved",
    "tested",
    "passes",
    "limit_reached",
    "negative_separation",
    "published_motion_violations",
    "motion_validation_incomplete",
    "symmetry_error",
)
CONTACT_WARNINGS = {
    "unresolved": "Skin contact projection retains unresolved contacts.",
    "limit_reached": "Skin contact projection reached its advisory work limit.",
    "motion_validation_incomplete": "Published skin motion validation is incomplete.",
}
VOLUME_LIMIT = (
    "Skin-anatomy volume penetration is not fully validated; "
    "sampled clearance is reported separately."
)


def checked(operation: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return operation()
    except (ValueError, RuntimeError, OSError, MemoryError) as error:
        if "cancel" in str(error).lower():
            raise
        return dict(incomplete=str(error))


def intersections(mesh: Any, cancel: int) -> dict[str, Any]:
    return checked(lambda: native.intersections(mesh, worker_memory.budget(), cancel))


def compare(before: Any, after: Any) -> dict[str, Any]:
    first = set(map(tuple, before.get("intersection_witnesses", ())))
    second = set(map(tuple, after.get("intersection_witnesses", ())))
    return dict(
        inherited_witnesses=len(first & second),
        new_witnesses=len(second - first),
        complete=(
            before.get("self_intersections", -1) == len(first)
            and after.get("self_intersections", -1) == len(second)
        ),
    )


def geometry(reference: Any, base: Any, mesh: Any, targets: Any, cancel: int) -> dict[str, Any]:
    baseline = json.loads(reference.metadata).get("reference_quality")
    baseline = intersections(base, cancel) if baseline is None else baseline
    current = intersections(mesh, cancel)
    clearance = checked(
        lambda: native.clearance(base, mesh, reference.arrays["samples"], targets, cancel)
    )
    return dict(
        reference_quality=baseline,
        intersections=current,
        anatomy_clearance=clearance,
        crossing_comparison=compare(baseline, current),
        topology_quality=checked(lambda: native.topology(mesh, cancel)),
    )


def metadata(reference: Any, diagnostics: Any, contact: Any, geometry: Any) -> dict[str, Any]:
    saved = json.loads(reference.metadata)
    solver = solver_report(saved, diagnostics)
    projection = {} if contact is None else dict(zip(CONTACT, map(float, contact), strict=True))
    warnings = solver_warnings(solver) + contact_warnings(projection) + geometry_warnings(geometry)
    return dict(
        kind="final_skin",
        reference=reference.digest,
        warnings=warnings,
        tissue_surface=saved["tissue_surface"],
        contact_coverage="incomplete",
        solver=solver,
        contact=projection,
        **geometry,
    )


def solver_report(saved: Any, diagnostics: Any) -> dict[str, Any]:
    info = dict(zip(SOLVER, map(float, diagnostics), strict=True))
    info["iteration_limit_reached"] = (
        saved["settings"]["method"] == "FAST" and info["iterations"] >= 80
    )
    return info


def solver_warnings(info: Any) -> list[str]:
    warnings = []
    if info["minimum_proxy_j"] <= 0:
        warnings.append("Deformation proxy has inverted elements.")
    if info["iteration_limit_reached"]:
        warnings.append("FAST reached its iteration limit; convergence is incomplete.")
    if info["outside_embeddings"]:
        count = int(info["outside_embeddings"])
        warnings.append(
            f"Reference proxy extrapolates {count} skin/anatomy embeddings outside its boundary."
        )
    return warnings


def contact_warnings(info: Any) -> list[str]:
    warnings = [text for key, text in CONTACT_WARNINGS.items() if info.get(key)]
    count = info.get("published_motion_violations", 0)
    if count > 0:
        warnings.append("Published skin motion contains contact violations.")
    if count < 0:
        warnings.append("Published skin motion validation is unavailable.")
    return warnings


def geometry_warnings(info: Any) -> list[str]:
    warnings = [
        f"Skin {key.replace('_', ' ')} diagnostic unavailable: {row['incomplete']}"
        for key, row in info.items()
        if isinstance(row, dict) and row.get("incomplete")
    ]
    intersections = info.get("intersections", {}).get("self_intersections", 0)
    if intersections:
        warnings.append(
            f"Skin has {intersections} self-intersections; compare with the retained reference."
        )
    if "anatomy_clearance" in info:
        warnings.append(VOLUME_LIMIT)
    return warnings
