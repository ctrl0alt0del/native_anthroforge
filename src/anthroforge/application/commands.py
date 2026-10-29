"""One explicit operation catalogue; no active Blender context or Python eval."""

from functools import partial
from typing import TYPE_CHECKING, Any

from anthroforge.core.units import convert

from . import (
    assembly_operations,
    attached_creation,
    comparison_journal,
    comparison_replay,
    construction_tasks,
    curve_branch_creation,
    curve_consumers,
    curve_conversion,
    curve_edit_operations,
    curve_independence,
    deletion_impact,
    drawing_operations,
    drawing_projection,
    driving_operations,
    evaluation,
    fiber_bindings,
    fiber_operations,
    fiber_pin_repairs,
    fiber_presentation,
    fiber_support_operations,
    geometry_modifiers,
    image_operations,
    image_presentation,
    importing,
    inspection,
    inspection_report,
    junction_operations,
    mesh_replacement,
    mirror_operations,
    object_operations,
    operations,
    output_tasks,
    parametric_operations,
    path_tasks,
    point_operations,
    presentation,
    projects,
    property_operations,
    quick_fiber,
    replacement_status,
    scp_splitting,
    segment_operations,
    shortcut_operations,
    shrinkwrap_operations,
    skeleton_operations,
    skin_collagen,
    skin_export,
    skin_fit_capture,
    skin_fit_jobs,
    skin_fit_preview,
    skin_fit_results,
    skin_jobs,
    skin_operations,
    skin_painting,
    skin_update_tasks,
    snap_tasks,
    surface_branch_operations,
    surface_correspondence,
    surface_grouping,
    surface_operations,
    surface_preview,
    surface_sources,
    symmetric_paths,
    tissue_field_operations,
    tissue_operations,
    tissue_painting,
    tissue_part_operations,
    tissue_preset_operations,
    tissue_preview,
    tissue_region_capture,
    tissue_retarget,
    tissue_stack_operations,
    tissue_strategy_operations,
)
from . import control_operations as controls
from . import deformer_operations as deformers
from . import primitive_operations as primitives
from .mirror_policy import require_edit
from .variant_operations import execute as variant_command
from .variant_policy import command as require_variant_command

if TYPE_CHECKING:
    from .session import Session

EDITS = {
    "skeleton_update.apply": skeleton_operations.apply,
    "assembly.import": assembly_operations.apply,
    "skin.collagen.paint.commit": skin_painting.commit,
    "skin.collagen.set": skin_collagen.set_weights,
    "skin.collagen.fill": skin_collagen.fill,
    "skin.collagen.clear": skin_collagen.clear,
    "skin.envelope.build": partial(skin_jobs.build, stage="envelope"),
    "skin.topology.build": partial(skin_jobs.build, stage="topology"),
    "skin.reference.build": partial(skin_jobs.build, stage="reference"),
    "skin.evaluate": skin_update_tasks.evaluate,
    "skin.fit": skin_fit_jobs.start,
    "skin.fit.authoring": partial(skin_fit_jobs.start, authoring=True),
    "skin.fit.remove": skin_fit_results.remove,
    "skin.build": skin_jobs.build,
    "skin.configure": skin_operations.configure,
    "skin.envelope.reset": skin_operations.reset_envelope,
    "skin.contributor.configure": skin_operations.contributor,
    "mirror.loop.create": symmetric_paths.create,
    "mirror.configure": mirror_operations.configure,
    "mirror.attachment.share": mirror_operations.share_target,
    "driver.create": driving_operations.create,
    "driver.configure": driving_operations.configure,
    "driver.value": driving_operations.set_value,
    "driver.remove": driving_operations.remove,
    "driver.formula.add": driving_operations.add_formula,
    "driver.formula.update": driving_operations.update_formula,
    "driver.formula.remove": driving_operations.remove_formula,
    "property.set": property_operations.set_value,
    "shortcut.expose": shortcut_operations.expose,
    "shortcut.configure": shortcut_operations.configure,
    "shortcut.set": shortcut_operations.set_value,
    "shortcut.reorder": shortcut_operations.reorder,
    "curve.parametric.configure": parametric_operations.configure,
    "curve.parametric.variable.add": parametric_operations.add_variable,
    "curve.parametric.variable.update": parametric_operations.update_variable,
    "curve.parametric.variable.remove": parametric_operations.remove_variable,
    "chain.configure": segment_operations.configure,
    "chain.segment": segment_operations.segment,
    "chain.resize": segment_operations.resize,
    "shrinkwrap.add": shrinkwrap_operations.add,
    "modifier.add": geometry_modifiers.add,
    "modifier.update": geometry_modifiers.update,
    "shrinkwrap.update": shrinkwrap_operations.update,
    "surface.snap.curves": snap_tasks.confirm,
    "surface.snap.points": snap_tasks.confirm_samples,
    "tissue.preview.accept": tissue_preview.accept,
    "tissue.stacking.configure": tissue_stack_operations.configure,
    "tissue.stacking.relationship": tissue_stack_operations.relationship,
    "tissue.stacking.remove": tissue_stack_operations.remove,
    "tissue.smoothing": tissue_part_operations.smoothing,
    "tissue.connector": tissue_part_operations.connector,
    "tissue.side.copy": tissue_part_operations.copy_side,
    "tissue.profile.reset": tissue_part_operations.profile_reset,
    "tissue.profile.scale": tissue_part_operations.profile_scale,
    "tissue.control.reset": tissue_part_operations.control_reset,
    "tissue.crop": tissue_strategy_operations.crop,
    "tissue.relaxation": tissue_strategy_operations.relaxation,
    "tissue.constraint.add": tissue_strategy_operations.constraint_add,
    "tissue.constraint.update": tissue_strategy_operations.constraint_update,
    "tissue.constraint.remove": tissue_strategy_operations.constraint_remove,
    "tissue.constraint.bind": tissue_region_capture.bind,
    "tissue.constraint.unlink": tissue_region_capture.unlink,
    "tissue.field.set": tissue_strategy_operations.field_set,
    "tissue.field.create": tissue_field_operations.create,
    "tissue.field.assign": tissue_field_operations.assign,
    "tissue.field.paint.commit": tissue_painting.commit,
    "tissue.field.remove": tissue_strategy_operations.field_remove,
    "tissue.create": tissue_operations.create,
    "tissue.configure": tissue_operations.configure,
    "tissue.preset.apply": tissue_preset_operations.apply,
    "tissue.source.replace.apply": tissue_retarget.apply,
    "tissue.inflation": tissue_operations.inflation,
    "construction.point.create": point_operations.create,
    "construction.point.update": point_operations.update,
    "anchor.create": point_operations.anchor,
    "anchor.rebind": point_operations.rebind,
    "surface.create": surface_operations.create,
    "surface.correspondence": surface_correspondence.configure,
    "membrane.create": attached_creation.membrane,
    "surface.update": surface_operations.update,
    "surface.source": surface_operations.source,
    "surface.sources": surface_sources.assign,
    "surface.source.add": surface_sources.add,
    "surface.source.remove": surface_sources.remove,
    "surface.order": surface_operations.order,
    "surface.realign": surface_operations.realign,
    "surface.preview.accept": surface_preview.accept,
    "surface.branch.add": surface_branch_operations.add,
    "surface.branch.remove": surface_branch_operations.remove,
    "fiber.create": fiber_operations.create,
    "fiber.place": quick_fiber.create,
    "fiber.binding.scope": fiber_operations.binding_scope,
    "fiber.binding.set": fiber_bindings.assign,
    "fiber.binding.remove": fiber_bindings.remove,
    "fiber.binding.offset": fiber_bindings.normal_offset,
    "fiber.rebind": fiber_bindings.rebind_all,
    "fiber.pins.repair": fiber_pin_repairs.apply,
    "fiber.supports.configure": fiber_support_operations.configure,
    "image.import": image_operations.import_image,
    "image.replace": image_operations.replace_source,
    "image.instance": image_operations.instance,
    "image.size": image_operations.size,
    "image.calibrate": image_operations.calibrate,
    "image.align": image_operations.align,
    "curve.create": object_operations.create_curve,
    "curve.branch.create": curve_branch_creation.create,
    "curve.draw": drawing_operations.draw,
    "curve.conversion.accept": curve_conversion.accept,
    "curve.edit": object_operations.edit_curve,
    "curve.engine_settings": curve_edit_operations.configure,
    "curve.engine": curve_edit_operations.change_engine,
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
    "consumer.sampling": curve_consumers.sampling,
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
    "scp.split": scp_splitting.split,
    "scp.mesh.replace.apply": mesh_replacement.apply,
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
    if operation.startswith(("property.", "shortcut.")) and operation not in EDITS:
        return shortcut_queries(session, operation, arguments)
    handler = query_handler(operation)
    if handler:
        return handler(session, operation, arguments)
    if operation in EDITS:
        return edit(session, operation, arguments)
    direct = direct_commands(session)
    if operation not in direct:
        raise ValueError(f"Unknown operation: {operation}")
    return comparison_journal.direct(session, operation, arguments, direct[operation])


def query_handler(operation: str) -> Any:
    if operation.startswith(("tissue.inspect.", "curve.inspect.", "skin.inspect.")):
        from .tissue_inspection import execute as tissue_inspect

        return tissue_inspect
    if operation.startswith(("measurement.", "bookmark.", "geometry.")):
        from .inspection_commands import execute as inspect_command

        return inspect_command
    if operation.startswith("issues."):
        from .issues.commands import execute as issue_command

        return issue_command
    return variant_command if operation.startswith("variant.") else None


def shortcut_queries(session: "Session", operation: str, arguments: dict[str, Any]) -> Any:
    from .shortcut_inspection import operations

    queries: dict[str, Any] = {
        **operations(),
        "property.discover": property_operations.discover,
        "property.get": property_operations.get,
        "shortcut.inspect": shortcut_operations.inspect,
        "shortcut.list": shortcut_operations.listing,
    }
    if operation not in queries:
        raise ValueError(f"Unknown shortcut/property operation: {operation}")
    return queries[operation](session, **arguments)


def edit(session: "Session", operation: str, arguments: dict[str, Any]) -> Any:
    require_command_edit(session, operation, arguments)
    implicit = session.history.before is None
    if implicit:
        session.begin()
    try:
        result = comparison_journal.edit(session, operation, arguments, EDITS[operation])
        if implicit:
            session.commit()
        return result
    except Exception:
        if implicit and session.history.before is not None:
            session.cancel()
        raise


def require_command_edit(session: "Session", operation: str, arguments: dict[str, Any]) -> None:
    require_edit(arguments)
    require_variant_command(session, operation, arguments)
    if (
        operation in {"assembly.import", "skeleton_update.apply"}
        and session.history.before is not None
    ):
        raise ValueError("Finish the current gesture before importing or resolving anatomy.")


def direct_commands(session: "Session") -> dict[str, Any]:
    return {
        **assembly_operations.commands(session),
        **skeleton_operations.commands(session),
        **file_commands(session),
        **query_commands(session),
        **history_commands(session),
        "inspect": session.describe,
        **skin_queries(session),
        "wait": session.wait,
        "tick": session.scheduler.tick,
        "evaluate": lambda **a: evaluate(session, **a),
        "curve.reroute": lambda **a: path_tasks.reroute(session, **a),
    }


def skin_queries(session: "Session") -> dict[str, Any]:
    return {
        "skin.inspect": lambda: skin_operations.inspect(session),
        "skin.report": lambda: skin_operations.report(session),
        "skin.status": session.skin_status.describe,
        "skin.export": lambda **a: skin_export.export(session, **a),
        **skin_fit_queries(session),
    }


def history_commands(session: "Session") -> dict[str, Any]:
    return {
        "begin": session.begin,
        "commit": session.commit,
        "cancel": session.cancel,
        "undo": lambda: session.navigate(-1),
        "redo": lambda: session.navigate(1),
    }


def skin_fit_queries(session: "Session") -> dict[str, Any]:
    return {
        "skin.fit.inspect": lambda **a: skin_fit_results.inspect(session, **a),
        "skin.fit.eligibility": lambda **a: skin_fit_capture.describe(session, **a),
        "skin.fit.preview": lambda **a: skin_fit_preview.request(session, **a),
        "skin.fit.preview.status": lambda: skin_fit_preview.status(session),
        "skin.fit.preview.cancel": lambda: skin_fit_preview.cancel(session),
    }


def query_commands(session: "Session") -> dict[str, Any]:
    return {
        **mirror_operations.queries(session),
        **preference_queries(session),
        "driver.inspect": lambda **a: driving_operations.inspect(session, **a),
        **drawing_commands(session),
        **construction_queries(session),
        "image.presentation": lambda **a: image_presentation.update(session, **a),
        "job.cancel": lambda job_id, obsolete=False: session.scheduler.cancel_job(job_id, obsolete),
        "job.retry": session.scheduler.retry,
        "inspect.target": lambda **a: inspection.target(session, **a),
        "inspect.snapshot": lambda **a: inspection.snapshot(session, **a),
        "object.delete.inspect": lambda **a: deletion_impact.inspect(session, **a),
        "units.convert": convert,
    }


def preference_queries(session: "Session") -> dict[str, Any]:
    return {
        "preferences.get": session.preferences.describe,
        "preferences.set": session.preferences.update,
    }


def construction_queries(session: "Session") -> dict[str, Any]:
    return {
        **tissue_queries(session),
        "tissue.stacking.inspect": lambda **a: tissue_stack_operations.inspect(session, **a),
        **surface_queries(session),
        "image.inspect": lambda **a: image_operations.inspect(session, **a),
        "object.inspect": lambda **a: object_operations.inspect(session, **a),
        **fiber_queries(session),
        "fiber.presentation": lambda **a: fiber_presentation.update(session, **a),
        "fiber.presentation.inspect": lambda **a: fiber_presentation.inspect(session, **a),
        "primitive.inspect": lambda **a: primitives.inspect(session, **a),
        "control.affected": lambda **a: controls.affected(session, **a),
        "deformer.members": lambda **a: deformers.members(session, **a),
        "junction.inspect": lambda **a: junction_operations.inspect(session, **a),
    }


def fiber_queries(session: "Session") -> dict[str, Any]:
    from .issues import fiber_pins

    return {
        "fiber.supports.inspect": lambda **a: fiber_support_operations.inspect(session, **a),
        "fiber.pins.check": lambda **a: fiber_pins.request(session, **a),
    }


def surface_queries(session: "Session") -> dict[str, Any]:
    return {
        **replacement_queries(session),
        "surface.source_ids": lambda **a: surface_sources.identities(session, **a),
        "surface.preview": lambda **a: surface_preview.preview(session, **a),
        "tissue.source.replace.assess": lambda **a: tissue_retarget.assess(session, **a),
        "tissue.source.replace.status": lambda: tissue_retarget.status(session),
        "tissue.source.replace.cancel": lambda: tissue_retarget.cancel(session),
        "scp.mesh.replace.assess": lambda **a: mesh_replacement.assess(session, **a),
        "scp.mesh.replace.status": lambda: mesh_replacement.status(session),
        "scp.mesh.replace.cancel": lambda: mesh_replacement.cancel(session),
        "surface.grouping": lambda **a: surface_grouping.inspect(session, **a),
        "surface.preview.status": lambda: surface_preview.status(session),
        "surface.preview.cancel": lambda: surface_preview.cancel(session),
    }


def replacement_queries(session: "Session") -> dict[str, Any]:
    return {
        "tissue.source.options": lambda **a: tissue_retarget.options(session, **a),
        "scp.mesh.replace.eligibility": lambda target: replacement_status.describe(
            session, "mesh_replacement", target
        ),
        "tissue.source.replace.eligibility": lambda target: replacement_status.describe(
            session, "tissue_retarget", target
        ),
    }


def tissue_queries(session: "Session") -> dict[str, Any]:
    return {
        "tissue.profile.scaled": lambda **a: tissue_part_operations.scaled_profile(session, **a),
        "tissue.preview": lambda **a: tissue_preview.preview(session, **a),
        "tissue.preview.status": lambda: tissue_preview.status(session),
        "tissue.preview.cancel": lambda: tissue_preview.cancel(session),
    }


def drawing_commands(session: "Session") -> dict[str, Any]:
    from . import cursor_placement

    return {
        "cursor.place.surface": lambda **a: cursor_placement.request(session, **a),
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
        "inspection.replay": lambda **a: comparison_replay.replay(**a),
        "open": lambda **a: projects.open_project(session, **a),
        "workspace.create": lambda **a: presentation.create_workspace(session, **a),
        "workspace.select": lambda **a: presentation.select_workspace(session, **a),
        "workspace.update": lambda **a: presentation.update_workspace(session, **a),
        "workspace.remove": lambda **a: presentation.remove_workspace(session, **a),
        "workspace.preset": lambda **a: presentation.preset(session, **a),
        **view_commands(session),
    }


def view_commands(session: "Session") -> dict[str, Any]:
    return {
        "view.hide": lambda **a: presentation.hide(session, **a),
        "view.isolate": lambda **a: presentation.isolate(session, **a),
        "view.show_all": lambda: presentation.update_workspace(session, hidden=[]),
    }


def evaluate(session: "Session", entities: list[str] | None = None) -> str:
    targets = (
        set(entities) if entities is not None else {item.id for item in session.document.entities}
    )
    curves = set(entities) if entities is not None else set(session.document.registry.authored)
    output_tasks.schedule(session, curves, explicit=True)
    construction_tasks.evaluate(session, entities)
    captures = {
        item.id
        for item in session.document.entities
        if item.status == "edited" or not item.attachment.binding
    }
    return evaluation.request(session, targets & session.document.index.entities.keys(), captures)
