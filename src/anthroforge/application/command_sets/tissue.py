"""Tissue operation declarations; common execution lives in command_execution."""

from .. import (
    replacement_status,
    tissue_field_operations,
    tissue_inspection,
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
from .. import tissue_inspection_stages as stages
from ..command_contracts import direct, edit, query
from ..issues import tissue_geometry

COMMANDS = (
    edit("tissue.preview.accept", tissue_preview.accept),
    edit("tissue.stacking.configure", tissue_stack_operations.configure),
    edit("tissue.stacking.relationship", tissue_stack_operations.relationship),
    edit("tissue.stacking.remove", tissue_stack_operations.remove),
    edit("tissue.smoothing", tissue_part_operations.smoothing),
    edit("tissue.connector", tissue_part_operations.connector),
    edit("tissue.side.copy", tissue_part_operations.copy_side),
    edit("tissue.profile.reset", tissue_part_operations.profile_reset),
    edit("tissue.profile.scale", tissue_part_operations.profile_scale),
    edit("tissue.control.reset", tissue_part_operations.control_reset),
    edit("tissue.crop", tissue_strategy_operations.crop),
    edit("tissue.relaxation", tissue_strategy_operations.relaxation),
    edit("tissue.constraint.add", tissue_strategy_operations.constraint_add),
    edit("tissue.constraint.update", tissue_strategy_operations.constraint_update),
    edit("tissue.constraint.remove", tissue_strategy_operations.constraint_remove),
    edit("tissue.constraint.bind", tissue_region_capture.bind),
    edit("tissue.constraint.unlink", tissue_region_capture.unlink),
    edit("tissue.field.set", tissue_strategy_operations.field_set),
    edit("tissue.field.create", tissue_field_operations.create),
    edit("tissue.field.assign", tissue_field_operations.assign),
    edit("tissue.field.paint.commit", tissue_painting.commit, isolated=True),
    edit("tissue.field.remove", tissue_strategy_operations.field_remove),
    edit("tissue.create", tissue_operations.create),
    edit("tissue.configure", tissue_operations.configure),
    edit("tissue.preset.apply", tissue_preset_operations.apply),
    edit("tissue.source.replace.apply", tissue_retarget.apply),
    edit("tissue.inflation", tissue_operations.inflation),
    direct(
        "tissue.stacking.inspect",
        lambda session, **a: tissue_stack_operations.inspect(session, **a),
    ),
    direct(
        "tissue.source.replace.assess", lambda session, **a: tissue_retarget.assess(session, **a)
    ),
    direct("tissue.source.replace.status", lambda session: tissue_retarget.status(session)),
    direct("tissue.source.replace.cancel", lambda session: tissue_retarget.cancel(session)),
    direct("tissue.source.options", lambda session, **a: tissue_retarget.options(session, **a)),
    direct(
        "tissue.source.replace.eligibility",
        lambda session, target: replacement_status.describe(session, "tissue_retarget", target),
    ),
    direct(
        "tissue.profile.scaled",
        lambda session, **a: tissue_part_operations.scaled_profile(session, **a),
    ),
    direct("tissue.preview", lambda session, **a: tissue_preview.preview(session, **a)),
    direct("tissue.preview.status", lambda session: tissue_preview.status(session)),
    direct("tissue.preview.cancel", lambda session: tissue_preview.cancel(session)),
    query("tissue.inspect.stages", stages.describe),
    query(
        "tissue.inspect.compare",
        lambda session, **arguments: tissue_inspection.start(session, "comparison", **arguments),
    ),
    query(
        "tissue.inspect.point",
        lambda session, **arguments: tissue_inspection.start(session, "point", **arguments),
    ),
    query(
        "tissue.inspect.stacking",
        lambda session, **arguments: tissue_inspection.start(session, "stacking", **arguments),
    ),
    query(
        "tissue.inspect.paint",
        lambda session, **arguments: tissue_inspection.start(session, "paint", **arguments),
    ),
    query(
        "tissue.inspect.section",
        lambda session, **arguments: tissue_inspection.start(session, "section", **arguments),
    ),
    query("tissue.inspect.status", tissue_inspection.status),
    query("tissue.inspect.cancel", tissue_inspection.cancel),
    query("tissue.inspect.check", tissue_geometry.request),
)
