"""Curves operation declarations; common execution lives in command_execution."""

from .. import (
    cursor_placement,
    curve_branch_creation,
    curve_consumers,
    curve_conversion,
    curve_edit_operations,
    curve_independence,
    drawing_operations,
    drawing_projection,
    junction_operations,
    object_operations,
    parametric_operations,
    path_tasks,
    tissue_inspection,
)
from ..command_contracts import direct, edit, query

COMMANDS = (
    edit("curve.parametric.configure", parametric_operations.configure),
    edit("curve.parametric.variable.add", parametric_operations.add_variable),
    edit("curve.parametric.variable.update", parametric_operations.update_variable),
    edit("curve.parametric.variable.remove", parametric_operations.remove_variable),
    edit("curve.create", object_operations.create_curve),
    edit("curve.branch.create", curve_branch_creation.create),
    edit("curve.draw", drawing_operations.draw),
    edit("curve.conversion.accept", curve_conversion.accept),
    edit("curve.edit", object_operations.edit_curve),
    edit("curve.engine_settings", curve_edit_operations.configure),
    edit("curve.engine", curve_edit_operations.change_engine),
    edit("curve.point.update", object_operations.edit_point),
    edit("curve.point.insert", curve_edit_operations.insert),
    edit("curve.point.remove", curve_edit_operations.remove),
    edit("curve.subdivide", curve_edit_operations.subdivide),
    edit("consumer.make_independent", curve_independence.make_independent),
    edit("consumer.sampling", curve_consumers.sampling),
    edit("junction.create", junction_operations.create),
    edit("junction.remove", junction_operations.remove),
    direct("curve.reroute", lambda session, **a: path_tasks.reroute(session, **a)),
    direct("junction.inspect", lambda session, **a: junction_operations.inspect(session, **a)),
    direct("cursor.place.surface", lambda session, **a: cursor_placement.request(session, **a)),
    direct("curve.conversion.preview", lambda session, **a: curve_conversion.preview(session, **a)),
    direct("curve.conversion.status", lambda session: curve_conversion.status(session)),
    direct("curve.conversion.cancel", lambda session: curve_conversion.cancel(session)),
    direct("drawing.project", lambda session, **a: drawing_projection.project(session, **a)),
    direct(
        "curve.evaluate",
        lambda session, curve: path_tasks.schedule(session, {curve}, explicit=True),
    ),
    query(
        "curve.inspect.route",
        lambda session, **arguments: tissue_inspection.start(session, "route", **arguments),
    ),
    query(
        "curve.inspect.status",
        lambda session, **arguments: tissue_inspection.status(session, "route", **arguments),
    ),
    query(
        "curve.inspect.cancel",
        lambda session, **arguments: tissue_inspection.cancel(session, "route", **arguments),
    ),
)
