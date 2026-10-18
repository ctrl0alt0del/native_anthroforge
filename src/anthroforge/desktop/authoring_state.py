"""Construction presentation projections and reusable native picking arrays."""

from dataclasses import fields

from anthroforge.application.control_frames import display_frame
from anthroforge.application.curve_sources import for_editing
from anthroforge.core.construction import Curve
from anthroforge.core.entities import IDENTITY
from anthroforge.core.objects import ConstructionObject
from anthroforge.native import bodies, components, construction
from anthroforge.native.scene import entity_frame

from . import curve_context


def data(editor):
    session, selected = editor.controller.session, editor.controller.selection
    entity = curve_context.owner(editor)
    control = session.document.index.controls.get(selected)
    item = entity or control
    result = projected_item(item, control is not None)
    result["is_control"] = control is not None
    if control:
        result["trs"] = session.engine.decompose(control.matrix)
    result["editing"] = editor.editing
    result["category"] = editor.category
    result["components"] = tuple(editor.selection)
    result["deformers"] = binding_records(item)
    result.update(construction_data(entity, session))
    return result


def projected_item(item, control):
    if item is None:
        return {}
    result = {
        field.name: getattr(item, field.name)
        for field in fields(item)
        if field.name not in ("points", "deformers", "attachment", "result")
    }
    result["attachment"] = getattr(item, "attachment", None)
    result["result"] = result_status(item.result)
    if not control and getattr(item, "primitive", None):
        result["primitive"] = primitive_parameters(item.primitive)
    return result


def primitive_parameters(primitive):
    return {f.name: getattr(primitive, f.name) for f in fields(primitive) if f.name != "curves"}


def result_status(result):
    return dict(status=result.status, error=result.error, pending=getattr(result, "pending", ()))


def binding_records(item):
    from anthroforge.application.membership import resolve

    if item is None:
        return []
    curves = {c.id: c for c in item.primitive.curves} if getattr(item, "primitive", None) else {}
    return [
        resolve(b, curves[b.target.component]) if b.target.stage == "CURVE" else b
        for b in getattr(item, "deformers", ())
    ]


def construction_data(entity, session):
    from anthroforge.application.construction_policy import topology_locks

    result = {}
    result["topology_dependents"] = (
        topology_locks(session.document, entity.id) if entity else []
    )
    result["standalone"] = isinstance(entity, Curve)
    result["curves"] = editor_curves(entity)
    result["controls"] = [
        dict(id=c.id, name=c.name, kind=c.kind) for c in session.document.controls
    ]
    return result


def editor_curves(item):
    from dataclasses import replace

    if isinstance(item, Curve):
        return (replace(item, matrix=IDENTITY),)
    definition = getattr(item, "primitive", None)
    return definition.curves if definition else ()


def selection_center(editor, selected):
    bounds = editor.controller.session.engine.bounds([value for p in selected for value in p])
    return [(bounds[i] + bounds[i + 3]) / 2 for i in range(3)]


def curve_components(session, entity, curve):
    records = construction.resolved_curve(session.engine, curve)
    local = records[:, [3, 4, 5, 0, 1, 2, 6, 7, 8]].reshape((-1, 3))
    frame = curve_context.frame(session, entity, curve)
    world = components.transformed(session.engine, local, frame)
    refs = [
        dict(owner=entity.id, curve=curve.id, point=p.id, part=part, index=i * 3 + j)
        for i, p in enumerate(curve.points)
        for j, part in enumerate(("left", "position", "right"))
    ]
    rows = list(zip(refs, world.tolist(), local.tolist(), strict=True))
    return (
        rows if curve.engine == "BEZIER" else [row for row in rows if row[0]["part"] == "position"]
    )


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
    entity = for_editing(session, entity)
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
    control = session.document.index.controls.get(selected)
    if control:
        return control_components(session, control)
    entity = curve_context.owner(editor)
    if isinstance(entity, Curve) and editor.editing:
        return curve_components(session, entity, entity)
    return entity_components(session, entity, editor.category) if entity and editor.editing else []


def base_components(session, entity, piece):
    entity = for_editing(session, entity)
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
    from .presentation import component

    available = {component_key(r[0]) for r in editor.rows if component(editor, r[0], True)}
    return [key for key in editor.selection if key in available]


def cache_key(editor):
    session, selected = editor.controller.session, editor.controller.selection
    item = session.document.registry.records.get(selected)
    return (
        selected,
        item.generation if item else -1,
        getattr(item, "pose_revision", 0),
        getattr(getattr(item, "result", None), "revision", 0),
        source_revisions(session, item),
        displayed_frame(session, item),
        editor.editing,
        editor.category,
        session.workspace.hidden_categories,
        session.workspace.unpickable_categories,
    )


def displayed_frame(session, item):
    if isinstance(item, ConstructionObject):
        from anthroforge.application.curve_sources import world

        return world(session.engine, session.document, item.id)
    return display_frame(session, item) if item and not hasattr(item, "primitive") else None


def source_revisions(session, item):
    if not getattr(item, "primitive", None):
        return ()
    return tuple(
        (session.document.object(c.id).generation, session.document.object(c.id).result.revision)
        for c in item.primitive.curves
    )


def imported_selection(editor):
    chosen = set(editor.selection)
    return any(
        ref["part"] in ("vertex", "base") and component_key(ref) in chosen
        for ref, _, _ in editor.rows
    )
