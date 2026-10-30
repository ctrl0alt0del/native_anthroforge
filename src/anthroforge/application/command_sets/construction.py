"""Construction operation declarations; common execution lives in command_execution."""

from .. import (
    deletion_impact,
    fiber_bindings,
    fiber_operations,
    fiber_pin_repairs,
    fiber_presentation,
    fiber_support_operations,
    image_operations,
    image_presentation,
    object_operations,
    point_operations,
    quick_fiber,
)
from ..command_contracts import direct, edit
from ..issues import fiber_pins as fiber_pins

COMMANDS = (
    edit("construction.point.create", point_operations.create),
    edit("construction.point.update", point_operations.update),
    edit("anchor.create", point_operations.anchor),
    edit("anchor.rebind", point_operations.rebind),
    edit("fiber.create", fiber_operations.create),
    edit("fiber.place", quick_fiber.create),
    edit("fiber.binding.scope", fiber_operations.binding_scope),
    edit("fiber.binding.set", fiber_bindings.assign),
    edit("fiber.binding.remove", fiber_bindings.remove),
    edit("fiber.binding.offset", fiber_bindings.normal_offset),
    edit("fiber.rebind", fiber_bindings.rebind_all),
    edit("fiber.pins.repair", fiber_pin_repairs.apply),
    edit("fiber.supports.configure", fiber_support_operations.configure),
    edit("image.import", image_operations.import_image),
    edit("image.replace", image_operations.replace_source),
    edit("image.instance", image_operations.instance),
    edit("image.size", image_operations.size),
    edit("image.calibrate", image_operations.calibrate),
    edit("image.align", image_operations.align),
    edit("object.rename", object_operations.rename),
    edit("object.transform", object_operations.transform),
    edit("object.reparent", object_operations.reparent),
    edit("object.delete", object_operations.delete),
    direct("image.presentation", lambda session, **a: image_presentation.update(session, **a)),
    direct("object.delete.inspect", lambda session, **a: deletion_impact.inspect(session, **a)),
    direct("image.inspect", lambda session, **a: image_operations.inspect(session, **a)),
    direct("object.inspect", lambda session, **a: object_operations.inspect(session, **a)),
    direct("fiber.presentation", lambda session, **a: fiber_presentation.update(session, **a)),
    direct(
        "fiber.presentation.inspect", lambda session, **a: fiber_presentation.inspect(session, **a)
    ),
    direct(
        "fiber.supports.inspect",
        lambda session, **a: fiber_support_operations.inspect(session, **a),
    ),
    direct("fiber.pins.check", lambda session, **a: fiber_pins.request(session, **a)),
)
