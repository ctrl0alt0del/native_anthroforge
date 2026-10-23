"""Move source body-space parameters through retained pelvis shaping cages."""

from math import degrees

from skeleton_shortcut_controls import reference
from skeleton_shortcut_formulae import calibrated, inputs, scaled_frame
from skeleton_shortcut_hooks import hidden

from anthroforge.native.construction import matrix

PARTS = (
    ("SCP_8", "pubis_geom", "pubis_arc", "SHORTCUT_10", ""),
    ("SCP_9", "ischium_geom", "ischium_curve", "", "SHORTCUT_12"),
    ("SCP_12", "ilium_geom", "ilium_arc", "SHORTCUT_14", "SHORTCUT_13"),
)


def flat(rows):
    return tuple(v for row in rows for v in row)


def rotation_frame(engine, geometry, guide):
    scale = engine.transform([0, 0, 0, 0, 0, 0, *geometry["scale"]])
    rotation = engine.transform([0, 0, 0, degrees(geometry["rotation"][0]), 0, 0, 1, 1, 1])
    inverse = matrix(
        engine, matrix(engine, rotation, scale), engine.transform([0] * 6 + [1] * 3), True
    )
    prefix = matrix(engine, flat(geometry["world"]), inverse)
    return matrix(engine, flat(guide["world"]), prefix, True)


def point_equations(engine, cage, piece, frame, ratios, gain, angle):
    base = engine.transform(
        [piece.length / 2, 0, 0, 0, 0, 0, piece.length, piece.width, piece.depth]
    )
    incoming = matrix(engine, frame, base, True)
    original = [engine.world_point(incoming, p) for p in cage.points]
    return [coordinate_equations(point, frame, piece, ratios, gain, angle) for point in original]


def coordinate_equations(point, frame, piece, ratios, gain, angle):
    x, y, z = point
    rotated = (
        f"{x!r}*({gain})",
        f"{y!r}*cos({angle})-{z!r}*sin({angle})",
        f"{y!r}*sin({angle})+{z!r}*cos({angle})",
    )
    result = []
    for axis, size in enumerate((piece.length, piece.width, piece.depth)):
        row = frame[axis * 4 : axis * 4 + 4]
        coordinate = "+".join(f"({row[i]!r})*({rotated[i]})" for i in range(3)) + f"+({row[3]!r})"
        origin = piece.length / 2 if axis == 0 else 0.0
        result.append(f"((({coordinate})/({ratios[axis]}))-{origin!r})/{size!r}*m")
    return result


def controls(session, target, ratios, mapping, incoming):
    entity, cage = session.document.entity(target), session.document.control(target + ":base-cage")
    scaled_frame(session, cage.id, mapping, ratios, incoming)
    length, use = entity.primitive.pieces[0].length, entity.primitive.curves[0]
    for axis in range(3):
        ref = reference(cage.id, "transform", "position", component=axis)
        delta = use.matrix[axis * 4] * length / 2
        calibrated(session, mapping, ref, f"{delta!r}*m*({ratios[0]}-1)", incoming, "m")


def names(sweep, bend):
    result = dict(radius="SHORTCUT_8", shrink="SHORTCUT_11")
    if sweep:
        result["sweep"] = sweep
    if bend:
        result["bend"] = bend
    return result


def body_parameters(mappings, sweep, bend):
    r, s = mappings["SHORTCUT_8"]["value"], mappings["SHORTCUT_11"]["value"]
    ratios = (f"radius/{r!r}", f"radius/{r!r}*shrink/{s!r}", f"radius/{r!r}")
    gain = f"(sweep/rad)*radius/({mappings[sweep]['value']!r}*{r!r})" if sweep else "1.0"
    angle = f"bend-{mappings[bend]['value']!r}*rad" if bend else "0*rad"
    return ratios, gain, angle


def cage_formulas(session, target, frame, ratios, gain, angle, mapping, incoming):
    cage = session.document.control(target + ":base-cage")
    piece = session.document.entity(target).primitive.pieces[0]
    equations = point_equations(session.engine, cage, piece, frame, ratios, gain, angle)
    for index, coordinates in enumerate(equations):
        for axis, expression in enumerate(coordinates):
            ref = reference(cage.id, "points", "#" + str(index), component=axis)
            calibrated(session, mapping, ref, expression, incoming, "m")


def migrate(session, mappings, captured):
    frames = {row["name"]: row for row in captured["objects"]}
    for owner, geometry, guide, sweep, bend in PARTS:
        frame = rotation_frame(session.engine, frames[geometry], frames[guide])
        ratios, gain, angle = body_parameters(mappings, sweep, bend)
        incoming = inputs(mappings, names(sweep, bend))
        mapping = mappings[bend or sweep]
        controls(session, owner, ratios, mapping, incoming)
        cage_formulas(session, owner, frame, ratios, gain, angle, mapping, incoming)
    sacrum(session, mappings)


def sacrum(session, mappings):
    mapping = hidden(session, "Sacrum width dependency")
    incoming = inputs(mappings, dict(radius="SHORTCUT_8", angle="SHORTCUT_10"))
    incoming.append(
        dict(name="volume_scale", property=reference("SCP_8", "world_transform", "volume_scale"))
    )
    ref = reference("SCP_10", "transform", "scale", component=0)
    calibrated(session, mapping, ref, "radius*sin(angle/2)*0.67*volume_scale", incoming)


def policies(session, mappings, definitions):
    for row in definitions["roots"]["AF_ROOT"]["shortcuts"]:
        if not row["overrides"] and not row["owner_backsolve"]:
            continue
        overrides = [override(r) for r in row["overrides"]]
        policy = dict(
            scope=row["owner_id"], backsolve=row["owner_backsolve"], descendants=overrides
        )
        session.command(
            "driver.configure", driver=mappings[row["id"]]["driver"], changes=dict(policy=policy)
        )


def override(row):
    return dict(
        target=row["target_scp_id"],
        parent_anchor=row["parent_anchor_mode"],
        child_anchor=row["child_anchor_mode"],
        follow_rotation=row["follow_rotation_mode"],
        strategy=row["rotation_strategy"],
    )
