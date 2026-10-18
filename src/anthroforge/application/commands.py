"""One explicit operation catalogue; no active Blender context or Python eval."""

from typing import TYPE_CHECKING, Any

from anthroforge.core.units import convert

from . import (
    construction_tasks,
    curve_consumers,
    curve_conversion,
    curve_edit_operations,
    curve_independence,
    drawing_operations,
    drawing_projection,
    evaluation,
    fiber_bindings,
    fiber_operations,
    image_operations,
    image_presentation,
    importing,
    inspection,
    inspection_report,
    junction_operations,
    object_operations,
    operations,
    path_tasks,
    presentation,
    projects,
    surface_branch_operations,
    surface_operations,
)
from . import control_operations as controls
from . import deformer_operations as deformers
from . import primitive_operations as primitives

if TYPE_CHECKING:
    from .session import Session

EDITS = {
    "surface.create": surface_operations.create,
    "surface.update": surface_operations.update,
    "surface.source": surface_operations.source,
    "surface.order": surface_operations.order,
    "surface.realign": surface_operations.realign,
    "surface.branch.add": surface_branch_operations.add,
    "surface.branch.remove": surface_branch_operations.remove,
    "fiber.create": fiber_operations.create,
    "fiber.binding.scope": fiber_operations.binding_scope,
    "fiber.binding.set": fiber_bindings.assign,
    "fiber.binding.remove": fiber_bindings.remove,
    "image.import": image_operations.import_image,
    "image.replace": image_operations.replace_source,
    "image.instance": image_operations.instance,
    "image.size": image_operations.size,
    "image.calibrate": image_operations.calibrate,
    "image.align": image_operations.align,
    "curve.create": object_operations.create_curve,
    "curve.draw": drawing_operations.draw,
    "curve.conversion.accept": curve_conversion.accept,
    "curve.edit": object_operations.edit_curve,
    "curve.engine_settings": curve_edit_operations.configure,
    "curve.point.update": object_operations.edit_point,
    "curve.point.insert": curve_edit_operations.insert,
    "curve.point.remove": curve_edit_operations.remove,
    "curve.subdivide": curve_edit_operations.subdivide,
    "object.rename": object_operations.rename,
    "object.transform": object_operations.transform,
    "object.reparent": object_operations.reparent,
    "object.delete": object_operations.delete,
    "primitive.from_curves": curve_consumers.from_curves,
    "primitive.curve_mode": curve_consumers.transform_mode,
    "primitive.curve_reverse": curve_consumers.reverse,
    "primitive.make_independent": curve_independence.make_independent,
    "consumer.make_independent": curve_independence.make_independent,
    "junction.create": junction_operations.create,
    "junction.remove": junction_operations.remove,
    "scp.empty": operations.empty,
    "scp.rename": operations.rename,
    "scp.color": operations.color,
    "scp.delete": operations.delete,
    "scp.duplicate": operations.duplicate,
    "scp.reparent": operations.reparent,
    "scp.wrap_root": operations.wrap_root,
    "scp.transform": operations.transform,
    "scp.attachment": operations.attachment,
    "scp.recapture": operations.recapture,
    "scp.origin": operations.move_origin,
    "attachments.enable": operations.toggle_attachments,
    "update_mode": operations.update_mode,
    "import": importing.import_mesh,
    "primitive.create": primitives.create,
    "primitive.update": primitives.update,
    "curve.update": primitives.curve_update,
    "curve.add": primitives.curve_add,
    "curve.remove": primitives.curve_remove,
    "curve.order": primitives.curve_order,
    "curve.split": primitives.curve_split,
    "point.update": primitives.point_update,
    "point.insert": primitives.point_insert,
    "point.remove": primitives.point_remove,
    "body.update": primitives.piece_update,
    "thickness.update": primitives.thickness,
    "control.create": controls.create,
    "control.transform": controls.transform,
    "control.follow": controls.follow,
    "control.update": controls.update,
    "control.delete": controls.delete,
    "lattice.point": controls.lattice_point,
    "lattice.resize": controls.lattice_resize,
    "deformer.add": deformers.add,
    "deformer.update": deformers.update,
    "deformer.remove": deformers.remove,
    "deformer.order": deformers.order,
    "hook.reset": deformers.reset,
    "hook.recenter": deformers.recenter,
}


def execute(session: "Session", operation: str, arguments: dict[str, Any]) -> Any:
    if operation.startswith(("measurement.", "bookmark.")):
        from .inspection_commands import execute as inspect_command

        return inspect_command(session, operation, arguments)
    if operation.startswith("issues."):
        from .issues.commands import execute as issue_command

        return issue_command(session, operation, arguments)
    if operation in EDITS:
        return edit(session, operation, arguments)
    direct = direct_commands(session)
    if operation not in direct:
        raise ValueError(f"Unknown operation: {operation}")
    return direct[operation](**arguments)


def edit(session: "Session", operation: str, arguments: dict[str, Any]) -> Any:
    implicit = session.history.before is None
    if implicit:
        session.begin()
    try:
        result = EDITS[operation](session, **arguments)  # type: ignore[operator]
        if implicit:
            session.commit()
        return result
    except Exception:
        if implicit and session.history.before is not None:
            session.cancel()
        raise


def direct_commands(session: "Session") -> dict[str, Any]:
    return {
        **file_commands(session),
        **query_commands(session),
        "begin": session.begin,
        "commit": session.commit,
        "cancel": session.cancel,
        "undo": lambda: session.navigate(-1),
        "redo": lambda: session.navigate(1),
        "inspect": session.describe,
        "wait": session.wait,
        "tick": session.scheduler.tick,
        "evaluate": lambda **a: evaluate(session, **a),
    }


def query_commands(session: "Session") -> dict[str, Any]:
    return {
        **drawing_commands(session),
        **construction_queries(session),
        "image.presentation": lambda **a: image_presentation.update(session, **a),
        "job.cancel": lambda job_id, obsolete=False: session.scheduler.cancel_job(job_id, obsolete),
        "job.retry": session.scheduler.retry,
        "inspect.target": lambda **a: inspection.target(session, **a),
        "inspect.snapshot": lambda **a: inspection.snapshot(session, **a),
        "units.convert": convert,
    }


def construction_queries(session: "Session") -> dict[str, Any]:
    return {
        "image.inspect": lambda **a: image_operations.inspect(session, **a),
        "object.inspect": lambda **a: object_operations.inspect(session, **a),
        "primitive.inspect": lambda **a: primitives.inspect(session, **a),
        "control.affected": lambda **a: controls.affected(session, **a),
        "deformer.members": lambda **a: deformers.members(session, **a),
        "junction.inspect": lambda **a: junction_operations.inspect(session, **a),
    }


def drawing_commands(session: "Session") -> dict[str, Any]:
    return {
        "curve.conversion.preview": lambda **a: curve_conversion.preview(session, **a),
        "curve.conversion.status": lambda: curve_conversion.status(session),
        "curve.conversion.cancel": lambda: curve_conversion.cancel(session),
        "drawing.project": lambda **a: drawing_projection.project(session, **a),
        "curve.evaluate": lambda curve: path_tasks.schedule(session, {curve}, explicit=True),
    }


def file_commands(session: "Session") -> dict[str, Any]:
    return {
        "save": lambda **a: projects.save(session, **a),
        "inspection.export": lambda **a: inspection_report.export(session, **a),
        "open": lambda **a: projects.open_project(session, **a),
        "workspace.create": lambda **a: presentation.create_workspace(session, **a),
        "workspace.select": lambda **a: presentation.select_workspace(session, **a),
        "workspace.update": lambda **a: presentation.update_workspace(session, **a),
        "workspace.remove": lambda **a: presentation.remove_workspace(session, **a),
        "workspace.preset": lambda **a: presentation.preset(session, **a),
    }


def evaluate(session: "Session", entities: list[str] | None = None) -> str:
    targets = (
        set(entities) if entities is not None else {item.id for item in session.document.entities}
    )
    curves = set(entities) if entities is not None else set(session.document.registry.construction)
    path_tasks.schedule(session, curves, explicit=True)
    construction_tasks.evaluate(session, entities)
    captures = {
        item.id
        for item in session.document.entities
        if item.status == "edited" or not item.attachment.binding
    }
    return evaluation.request(session, targets & session.document.index.entities.keys(), captures)
