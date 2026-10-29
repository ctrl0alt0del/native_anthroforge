"""Stable import list projection and compatible destination choices."""

from dataclasses import asdict

from anthroforge.application import assembly_mapping

from . import mapping_projection


def synchronize(panel):
    state = panel._state
    if not panel.repair:
        panel._references = list(state.get("mappings", ()))
        inventory = state.get("inventory", ())
        for model, anatomy in ((panel.anatomy, True), (panel.construction, False)):
            model.synchronize(
                [choice(row, panel) for row in inventory if row["anatomy"] == anatomy]
            )
    else:
        panel._references = pending(panel)
    if panel.focus and not any(r["key"] == panel.focus for r in panel._references):
        panel.focus = ""
    if not panel.focus and panel._references:
        panel.selectReference(panel._references[0]["key"])


def choice(row, panel):
    reason = panel._state.get("selection", {}).get(row["id"], "")
    explicit = row["id"] in panel.selected
    return dict(
        key=row["id"],
        label=row["name"],
        detail=row["kind"],
        chosen=explicit or bool(reason),
        locked=bool(reason) and not explicit,
        reason=reason if not explicit else "Selected",
    )


def pending(panel):
    return [
        pending_row(r, panel.mappings.get(r.id, {}))
        for r in panel.controller.session.document.external_references
        if not r.target and r.uses
    ]


def pending_row(r, choice):
    return dict(
        key=r.id,
        source=r.id,
        name=r.name + (" · mirrored" if r.source_instance else ""),
        kind=r.kind,
        role=r.uses[0].role,
        relationship=r.uses[0].relationship,
        property=repaired_property(r),
        **assembly_mapping.choice_details(choice),
    )


def signature(manager):
    return (
        manager.source.token,
        manager.source.state,
        manager.preparation.token,
        manager.preparation.state,
    )


def repaired_property(reference):
    return dict(asdict(reference.property), target=reference.id) if reference.property else None


def targets(panel):
    return mapping_projection.rows(panel, "assembly")


def properties(panel, target):
    return mapping_projection.rows(panel, "assembly", properties=True, target=target)


def parents(panel):
    return [dict(id=e.id, name=e.name) for e in panel.controller.session.document.entities]
