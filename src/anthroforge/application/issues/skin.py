"""Publish already-computed skin findings; never repeat expensive geometry checks."""

import json
from typing import Any

from anthroforge.core.issues import Issue, evidence, fingerprint

from .providers import Provider

NAME = "skin.v1"
STAGES = ("envelope", "topology", "final")
TOPOLOGY_LABELS = {
    "orientable": "Skin topology orientation is inconsistent",
    "manifold": "Skin topology has nonmanifold edges",
    "no_degenerates": "Skin topology has degenerate faces",
    "boundary_match": "Skin topology has unexpected boundary loops",
    "guide_preserved": "Skin topology did not retain every LOOP guide face",
    "symmetry_ok": "Skin topology differs from the selected symmetry plane",
    "fidelity_ok": "Skin topology departs from the envelope",
    "valence_ok": "Skin topology has vertices with more than eight neighbors",
}


def source(document: Any, scope: str) -> Any:
    skin = document.skin
    return (
        str(document.id),
        skin.construction_stale,
        skin.build_error,
        tuple((name, getattr(skin, name)) for name in STAGES),
    )


def capture(session: Any, document: Any) -> Any:
    keys = {getattr(document.skin, name).data for name in STAGES} - {""}
    return document, {
        key: session.resources.skin[key] for key in keys if key in session.resources.skin
    }


def provider(session: Any) -> Provider:
    return Provider(
        NAME,
        lambda _: {"document"},
        lambda d, c: {"document"} if "skin" in c.document else set(),
        source,
        check,
        lambda document: capture(session, document),
    )


def check(context: Any, scope: str, cancel: Any) -> tuple[Issue, ...]:
    document, assets = context
    rows = failure_findings(document)
    for name in STAGES:
        if cancel.is_set():
            break
        stage = getattr(document.skin, name)
        data = assets.get(stage.data)
        if data:
            rows.extend(stage_findings(document, name, stage, json.loads(data.metadata)))
    return tuple(rows)


def failure_findings(document: Any) -> list[Issue]:
    rows = []
    for name in STAGES:
        stage = getattr(document.skin, name)
        if stage.error:
            rows.append(finding(document, name, "SKIN_STAGE_FAILED", stage.error, {}))
    if document.skin.build_error:
        rows.append(finding(document, "build", "SKIN_BUILD_FAILED", document.skin.build_error, {}))
    return rows


def finding(document: Any, name: str, code: str, text: str, details: Any) -> Issue:
    return Issue(
        NAME,
        "document",
        code,
        text,
        stage=name,
        source=fingerprint(source(document, "document")),
        evidence=evidence(**details),
        local_key=text,
    )


def stage_findings(document: Any, name: str, stage: Any, metadata: Any) -> list[Issue]:
    details = stage_evidence(stage, metadata)
    messages = computed_messages(metadata)
    if stage.pending:
        messages.append(
            ("SKIN_PENDING_INPUT", "Skin uses accepted results with pending source edits")
        )
    if document.skin.construction_stale and name in ("topology", "final"):
        messages.append(
            ("SKIN_REBUILD_REQUIRED", "Skin construction changed; rebuild to use the new settings")
        )
    return [finding(document, name, code, text, details) for code, text in messages]


def stage_evidence(stage: Any, metadata: Any) -> dict[str, Any]:
    return dict(
        revision=stage.revision,
        geometry=stage.asset,
        quality=metadata.get("quality", {}),
        topology_quality=metadata.get("topology_quality", {}),
    )


def computed_messages(metadata: Any) -> list[tuple[str, str]]:
    messages = [("SKIN_CAPTURE_WARNING", warning) for warning in metadata.get("warnings", ())]
    messages.extend(quality_messages(metadata.get("quality", {})))
    return messages + topology_messages(metadata.get("topology_quality", {}))


def topology_messages(quality: Any) -> list[tuple[str, str]]:
    rows = [
        ("SKIN_TOPOLOGY_QUALITY", text)
        for key, text in TOPOLOGY_LABELS.items()
        if quality.get(key) == 0
    ]
    if quality.get("components", 0) > 1:
        rows.append(("SKIN_TOPOLOGY_COMPONENTS", "Skin topology contains disconnected components"))
    return rows


def quality_messages(quality: Any) -> list[tuple[str, str]]:
    rows = []
    for key in quality.get("unavailable", ()):
        rows.append(("SKIN_CHECK_UNAVAILABLE", "Skin check unavailable: " + key.replace("_", " ")))
    mesh = quality.get("mesh_quality") or {}
    labels = {
        "watertight": "Skin has open boundaries",
        "orientable": "Skin orientation is inconsistent",
        "positive_volume": "Skin has nonpositive signed volume",
        "no_degenerates": "Skin has degenerate faces",
    }
    rows.extend(("SKIN_MESH_QUALITY", text) for key, text in labels.items() if mesh.get(key) == 0)
    if quality.get("source_intersections", 0):
        rows.append(("SKIN_SOURCE_INTERSECTIONS", "Skin sources contain intersecting triangles"))
    return rows + coverage_messages(quality.get("coverage") or {})


def coverage_messages(coverage: Any) -> list[tuple[str, str]]:
    rows = []
    if coverage.get("source_vertices_outside", 0) or coverage.get("source_triangles_crossed", 0):
        rows.append(
            ("SKIN_SOURCE_COVERAGE", "Some source geometry extends outside the skin envelope")
        )
    if coverage.get("protected_gap_violations", 0):
        rows.append(("SKIN_GAP_COVERAGE", "Some protected gaps are covered by skin"))
    return rows
