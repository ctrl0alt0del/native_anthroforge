"""Field selection is presentation; weight assignment uses the shared operation policy."""

from anthroforge.application import tissue_fields
from anthroforge.application.object_frames import Frames
from anthroforge.native import components


def records(editor, item):
    session, name = editor.controller.session, editor.tissue_context[0]
    field = next((f for f in item.fields if f.name == name), None)
    if field is None:
        return []
    tissue_fields.validate(session.resources, item, field.domain)
    local = tissue_fields.positions(session, item, field.domain)
    world = components.transformed(
        session.engine, local, Frames(session.engine, session.document).world(item.id)
    )
    references = [reference(item, field, i, w) for i, w in enumerate(field.values)]
    return list(zip(references, world.tolist(), local.tolist(), strict=True))


def reference(item, field, index, weight):
    return dict(
        owner=item.id,
        piece=field.topology + field.name,
        part="field",
        index=index,
        field=field.name,
        topology=field.topology,
        weight=weight,
    )


def edit(editor, name):
    editor.tissue_context = (name, "")
    editor.category, editor.editing, editor.selection = "TISSUE_FIELD", True, []
    editor.refresh()


def assign(editor, value):
    chosen = [
        r for r in editor.componentRows if r["key"] in editor.selection and r["part"] == "field"
    ]
    if not chosen:
        return
    editor.controller.run("tissue.field.assign", assignment(chosen, value))


def assignment(chosen, value):
    first = chosen[0]
    return dict(
        target=first["owner"],
        name=first["field"],
        topology=first["topology"],
        indices=[r["index"] for r in chosen],
        value=value,
    )
