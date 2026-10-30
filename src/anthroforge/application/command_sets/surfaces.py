"""Surfaces operation declarations; common execution lives in command_execution."""

from .. import (
    attached_creation,
    snap_tasks,
    surface_branch_operations,
    surface_correspondence,
    surface_grouping,
    surface_operations,
    surface_options,
    surface_preview,
    surface_sources,
)
from ..command_contracts import direct, edit

COMMANDS = (
    edit("surface.snap.curves", snap_tasks.confirm),
    edit("surface.snap.points", snap_tasks.confirm_samples),
    edit("surface.create", surface_operations.create),
    edit("surface.correspondence", surface_correspondence.configure),
    edit("membrane.create", attached_creation.membrane),
    edit("surface.update", surface_operations.update),
    edit("surface.source", surface_operations.source),
    edit("surface.sources", surface_sources.assign),
    edit("surface.source.add", surface_sources.add),
    edit("surface.source.remove", surface_sources.remove),
    edit("surface.order", surface_operations.order),
    edit("surface.realign", surface_operations.realign),
    edit("surface.preview.accept", surface_preview.accept),
    edit("surface.branch.add", surface_branch_operations.add),
    edit("surface.branch.remove", surface_branch_operations.remove),
    direct("surface.source_ids", lambda session, **a: surface_sources.identities(session, **a)),
    direct("surface.preview", lambda session, **a: surface_preview.preview(session, **a)),
    direct("surface.grouping", lambda session, **a: surface_grouping.inspect(session, **a)),
    direct("surface.preview.status", lambda session: surface_preview.status(session)),
    direct("surface.preview.cancel", lambda session: surface_preview.cancel(session)),
    direct("surface.options", surface_options.options),
)
