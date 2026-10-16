"""Construction presentation projections and reusable native picking arrays."""

from dataclasses import asdict, fields

from anthroforge.application.control_frames import display_frame
from anthroforge.native import bodies, components, construction
from anthroforge.native.scene import entity_frame

from .values import qml


def data(editor):
    session, selected = editor.controller.session, editor.controller.selection
    entity = next((e for e in session.document.entities if e.id == selected), None)
    control = next((c for c in session.document.controls if c.id == selected), None)
    item = entity or control
    result = projected_item(item, control is not None)
    result["is_control"] = control is not None
    if control:
        result["trs"] = session.engine.decompose(control.matrix)
    result["editing"] = editor.editing
    result["category"] = editor.category
    result["components"] = editor.selection
    result["deformers"] = binding_records(item)
    result.update(construction_data(entity, session))
    return qml(result)


def projected_item(item, control):
    if item is None:
        return {}
    if not control:
        return asdict(item)
    result = {
        field.name: getattr(item, field.name)
        for field in fields(item)
        if field.name not in ("points", "deformers", "attachment", "result")
    }
    result["attachment"] = asdict(item.attachment)
    result["result"] = dict(status=item.result.status, error=item.result.error)
    return result


def binding_records(item):
    from anthroforge.application.membership import resolve

    if item is None:
        return []
    curves = {c.id: c for c in item.primitive.curves} if getattr(item, "primitive", None) else {}
    return [
        asdict(resolve(b, curves[b.target.component])) if b.target.stage == "CURVE" else asdict(b)
        for b in item.deformers
    ]


def construction_data(entity, session):
    from anthroforge.application.construction_policy import topology_dependents

    result = {}
    result["topology_dependents"] = (
        list(topology_dependents(session.document, entity.id)) if entity else []
    )
    result["curves"] = (
        [asdict(c) for c in entity.primitive.curves] if entity and entity.primitive else []
    )
    result["controls"] = [
        dict(id=c.id, name=c.name, kind=c.kind) for c in session.document.controls
    ]
    return result


def selection_center(editor, selected):
    bounds = editor.controller.session.engine.bounds([value for p in selected for value in p])
    return [(bounds[i] + bounds[i + 3]) / 2 for i in range(3)]


def curve_components(session, entity, curve):
    records = construction.resolved_curve(session.engine, curve)
    local = records[:, [3, 4, 5, 0, 1, 2, 6, 7, 8]].reshape((-1, 3))
    frame = construction.matrix(session.engine, entity_frame(session.engine, entity), curve.matrix)
    world = components.transformed(session.engine, local, frame)
    refs = [
        dict(owner=entity.id, curve=curve.id, point=p.id, part=part, index=i * 3 + j)
        for i, p in enumerate(curve.points)
        for j, part in enumerate(("left", "position", "right"))
    ]
    return list(zip(refs, world.tolist(), local.tolist(), strict=True))


def control_components(session, control):
    frame = display_frame(session, control)
    local = control.points if control.kind == "LATTICE" else ((0, 0, 0),)
    world = components.transformed(session.engine, local, frame)
    refs = [
        dict(owner=control.id, index=i, part="lattice" if control.kind == "LATTICE" else "control")
        for i in range(len(local))
    ]
    return list(zip(refs, world.tolist(), local, strict=True))


def entity_components(session, entity, category):
    if not entity.primitive:
        return []
    if entity.primitive.kind == "BODY" and category == "BASE":
        return [row for p in entity.primitive.pieces for row in base_components(session, entity, p)]
    if entity.primitive.kind == "IMPORTED":
        return imported_components(session, entity)
    return [
        row for curve in entity.primitive.curves for row in curve_components(session, entity, curve)
    ]


def imported_components(session, entity):
    mesh = session.assets[entity.primitive.source].mesh
    world = components.transformed(
        session.engine, mesh.array(0), entity_frame(session.engine, entity)
    )
    return [
        (dict(owner=entity.id, index=i, part="vertex"), p, local.tolist())
        for i, (p, local) in enumerate(zip(world.tolist(), mesh.array(0), strict=True))
    ]


def components_for(editor):
    session, selected = editor.controller.session, editor.controller.selection
    control = next((c for c in session.document.controls if c.id == selected), None)
    if control:
        return control_components(session, control)
    entity = next((e for e in session.document.entities if e.id == selected), None)
    return entity_components(session, entity, editor.category) if entity and editor.editing else []


def base_components(session, entity, piece):
    curve = next(c for c in entity.primitive.curves if c.id == piece.curve)
    mesh = bodies.base(session.engine, piece, entity.primitive.samples, curve.closed, 0)
    frame = construction.matrix(session.engine, entity_frame(session.engine, entity), curve.matrix)
    world = components.transformed(session.engine, mesh.array(0), frame).tolist()
    return [
        (dict(owner=entity.id, piece=piece.id, index=i, part="base"), p, local.tolist())
        for i, (p, local) in enumerate(zip(world, mesh.array(0), strict=True))
    ]


def component_key(reference):
    fields = (
        ("owner", "curve", "point", "part")
        if reference.get("point")
        else ("owner", "piece", "part", "index")
    )
    return ":".join(str(reference.get(key, "")) for key in fields)


def retained_selection(editor):
    available = {component_key(row[0]) for row in editor.rows}
    return [key for key in editor.selection if key in available]


def cache_key(editor):
    session, selected = editor.controller.session, editor.controller.selection
    items = (*session.document.entities, *session.document.controls)
    item = next((value for value in items if value.id == selected), None)
    return (
        selected,
        item.generation if item else -1,
        getattr(item, "pose_revision", 0),
        display_frame(session, item) if item and not hasattr(item, "primitive") else None,
        editor.editing,
        editor.category,
    )


def imported_selection(editor):
    chosen = set(editor.selection)
    return any(
        ref["part"] in ("vertex", "base") and component_key(ref) in chosen
        for ref, _, _ in editor.rows
    )
