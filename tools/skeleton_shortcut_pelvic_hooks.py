"""Compact source body-space changes through existing native Hook-on-lattice evaluation."""

from skeleton_shortcut_controls import reference
from skeleton_shortcut_formulae import calibrated, inputs
from skeleton_shortcut_pelvis import PARTS, body_parameters, controls, names, rotation_frame, sacrum

from anthroforge.application.control_operations import add
from anthroforge.core.construction import Control
from anthroforge.native.construction import matrix


def frame_controls(session, owner, frame):
    entity = session.document.entity(owner)
    identity, motion = owner + ":driver-frame", owner + ":driver-motion"
    placement = matrix(session.engine, entity.primitive.curves[0].matrix, frame)
    settings = dict(id=identity, follow=owner, owners=(owner,), matrix=placement)
    add(session, Control(entity.name + " driver frame", **settings))
    add(
        session,
        Control(entity.name + " body parameters", id=motion, follow=identity, owners=(owner,)),
    )
    session.command(
        "deformer.add", control=motion, target=dict(owner=owner + ":base-cage", stage="LATTICE")
    )
    return motion


def motion_formulas(session, motion, gain, angle, mapping, incoming):
    scale = reference(motion, "transform", "scale", component=0)
    rotation = reference(motion, "transform", "rotation", component=0)
    calibrated(session, mapping, scale, gain, incoming)
    calibrated(session, mapping, rotation, angle, incoming, "rad")


def migrate(session, mappings, captured):
    frames = {row["name"]: row for row in captured["objects"]}
    for owner, geometry, guide, sweep, bend in PARTS:
        frame = rotation_frame(session.engine, frames[geometry], frames[guide])
        ratios, gain, angle = body_parameters(mappings, sweep, bend)
        incoming = inputs(mappings, names(sweep, bend))
        mapping = mappings[bend or sweep]
        motion = frame_controls(session, owner, frame)
        controls(session, owner, ratios, mapping, incoming)
        motion_formulas(session, motion, gain, angle, mapping, incoming)
    sacrum(session, mappings)
