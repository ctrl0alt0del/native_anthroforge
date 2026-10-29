"""Matching and external-reference presentation use application compatibility policies."""

import json

from anthroforge.application import assembly_choices


def summary(state):
    heavy = {"inventory", "controls", "comparison", "evidence", "identities", "changes"}
    value = {key: item for key, item in state.items() if key not in heavy}
    value["checks"] = state.get("comparison", {}).get("checks", [])
    return value


def packet(panel):
    return json.dumps(
        dict(
            inventory=panel._state.get("inventory", []),
            controls=panel._state.get("controls", []),
            affected=panel._affected,
            attachments=panel._attachments,
        ),
        separators=(",", ":"),
    )


def review(state):
    rows = state.get("comparison", {}).get("rows", [])
    kinds = {r["id"]: (r["after"] or {}).get("kind") for r in rows}
    attachments = [point for r in state.get("evidence", []) for point in attachment_rows(r, kinds)]
    return [affected(r) for r in rows], attachments


def affected(row):
    after = row["after"] or {}
    return dict(
        id=row["id"],
        name=row["name"],
        changes=row["changes"],
        distance=row["distance"],
        after=dict(
            kind=after.get("kind"),
            geometry=dict(kind=after.get("geometry", {}).get("kind")),
            result={
                k: v for k, v in (after.get("result") or {}).items() if k in ("status", "error")
            },
        ),
    )


def attachment_rows(row, kinds):
    before = {r["point"]: r for r in row.get("before", [])}
    return [
        dict(
            owner=row["owner"],
            name=row.get("name", row["owner"]),
            point=p,
            before=before.get(p["point"]),
            editable=p["point"] != row["owner"] or kinds.get(row["owner"]) == "ANCHOR",
        )
        for p in row.get("after", [])
    ]


def synchronize(panel):
    panel._references = list(panel._state.get("mappings", ()))
    if not panel.initialized and panel._state.get("source_state") == "ready":
        panel.initialized = True
        panel.matches = {
            r["source"]: r["suggested"] for r in panel._state["inventory"] if r["suggested"]
        }
        if panel.matches:
            panel.queue()
    if panel._references and panel.focus not in {r["key"] for r in panel._references}:
        panel.selectReference(panel._references[0]["key"])


def parents(panel):
    return [dict(id=e.id, name=e.name) for e in panel.controller.session.document.entities]


def targets(panel):
    row = panel.current()
    return assembly_choices.targets(panel.controller.session.document, row) if row else []


def properties(panel):
    row = panel.current()
    if not row.get("property"):
        return []
    session = panel.controller.session
    source = session.skeleton_update.runtime.source.source.document
    return assembly_choices.properties(source, session.document, row, panel.target["target"])


def control_properties(panel, key, target):
    candidate = panel.controller.session.skeleton_update.runtime.preparation.candidate
    row = next((r for r in panel._state.get("controls", ()) if r["key"] == key), None)
    if candidate is None or row is None:
        return []
    return assembly_choices.properties(candidate.baseline, candidate.document, row, target)
