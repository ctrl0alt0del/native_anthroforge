"""Matching and external-reference presentation use application compatibility policies."""

from anthroforge.application import assembly_choices


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
