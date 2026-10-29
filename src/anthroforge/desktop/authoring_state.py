"""Construction presentation projections and reusable native picking arrays."""

from dataclasses import fields

from anthroforge.application.control_frames import display_frame
from anthroforge.application.curve_sources import for_editing
from anthroforge.core.component_reads import component_key as component_key
from anthroforge.core.construction import Curve
from anthroforge.core.construction_capabilities import component_editing, stable_geometry_members
from anthroforge.core.entities import IDENTITY
from anthroforge.core.objects import ConstructionObject
from anthroforge.core.tissues import TissueVCP

from . import curve_context, tissue_components

READ_ONLY_PARTS = frozenset(("vertex", "base", "field"))


def data(editor):
    session = editor.controller.session
    entity, control = inspection_owners(editor)
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


def inspection_owners(editor):
    from anthroforge.core.mirroring import source

    session, selected = editor.controller.session, editor.controller.selection
    control = session.document.index.controls.get(source(selected))
    entity = curve_context.owner(editor)
    if selected != source(selected) and not control:
        entity = session.document.object(source(selected))
        if hasattr(entity, "primitive"):
            entity = for_editing(session, entity)
    return entity, control


def projected_item(item, control):
    if item is None:
        return {}
    if isinstance(item, TissueVCP):
        return tissue_components.projected(item)
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

    from .curve_usage import uses

    result = editing_capabilities(entity)
    result["topology_dependents"] = topology_locks(session.document, entity.id) if entity else []
    result["standalone"] = isinstance(entity, Curve)
    result["curves"] = editor_curves(entity)
    result["uses"] = uses(session, entity)
    result["controls"] = [
        dict(id=c.id, name=c.name, kind=c.kind) for c in session.document.controls
    ]
    return result


def editing_capabilities(item):
    return dict(
        component_editing=component_editing(item),
        stable_geometry_members=stable_geometry_members(item),
    )


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
    from anthroforge.application.component_buffers import curve as resolve
    from anthroforge.application.editing_queries import rows
    from anthroforge.core.component_reads import ComponentRead

    return rows(ComponentRead("", (resolve(session, entity, curve),), ()))


def components_for(editor):
    from anthroforge.application import editing_queries

    session, target = editor.controller.session, editor.controller.selection
    if not target or not (editor.editing or target in session.document.index.controls):
        return []
    context = dict(part=editor.tissue_context[0], side=editor.tissue_context[1])
    if editor.category == "TISSUE_FIELD":
        context = dict(field=editor.tissue_context[0])
    return editing_queries.rows(editing_queries.current(session, target, editor.category, context))


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
        (editor.category, editor.tissue_context),
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


def read_only_selection(editor):
    chosen = set(editor.selection)
    return any(
        (ref["part"] in READ_ONLY_PARTS or ref.get("readonly")) and component_key(ref) in chosen
        for ref, _, _ in editor.rows
    )
