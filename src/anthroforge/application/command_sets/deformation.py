"""Deformation operation declarations; common execution lives in command_execution."""

from .. import control_operations as controls
from .. import deformer_operations as deformers
from .. import geometry_modifiers, shrinkwrap_operations
from ..command_contracts import direct, edit

COMMANDS = (
    edit("shrinkwrap.add", shrinkwrap_operations.add),
    edit("modifier.add", geometry_modifiers.add),
    edit("modifier.update", geometry_modifiers.update),
    edit("shrinkwrap.update", shrinkwrap_operations.update),
    edit("control.create", controls.create),
    edit("control.transform", controls.transform),
    edit("control.follow", controls.follow),
    edit("control.update", controls.update),
    edit("control.delete", controls.delete),
    edit("lattice.point", controls.lattice_point),
    edit("lattice.resize", controls.lattice_resize),
    edit("deformer.add", deformers.add),
    edit("deformer.update", deformers.update),
    edit("deformer.remove", deformers.remove),
    edit("deformer.order", deformers.order),
    edit("hook.reset", deformers.reset),
    edit("hook.recenter", deformers.recenter),
    direct("control.affected", lambda session, **a: controls.affected(session, **a)),
    direct("deformer.members", lambda session, **a: deformers.members(session, **a)),
)
