"""Retain source coordinate frames for Hook controls and paired-bone drivers."""

import re

from skeleton_shortcut_controls import driver, formula, reference

from anthroforge.application.object_frames import Frames
from anthroforge.native.construction import matrix


def value(session, ref):
    return session.command("property.get", reference=ref)["value"]


def hidden(session, label, initial=0.0, dimension="SCALAR"):
    key = session.command("driver.create", label=label, value=initial, dimension=dimension)
    session.command("driver.configure", driver=key, changes=dict(exposed=False))
    return dict(driver=key, value=initial, formulas=[])


def uniform_hooks(session, rows):
    result = []
    for key in ("SHORTCUT_100", "SHORTCUT_101", "SHORTCUT_102"):
        row = rows[key]
        target = "hook:" + row["resolved"]["id"]["id"]
        initial = row["resolved"]["captured"]["value"][0]
        mapping = hidden(session, row["name"], initial)
        session.command("driver.configure", driver=mapping["driver"], changes=dict(exposed=True))
        mapping["source"] = key
        for axis in range(3):
            ref = reference(target, "transform", "scale", component=axis)
            base = value(session, ref)
            formula(session, mapping, ref, f"{base!r} + (value-{initial!r})*{base / initial!r}")
        result.append(mapping)
    return result


def local_frame(session, target, source_frame):
    control = session.document.control(target)
    current = Frames(session.engine, session.document).world(control.follow)
    return matrix(session.engine, current, source_frame, relative=True)


def rib_hooks(session, rows, frames):
    result = []
    for key in ("SHORTCUT_6", "SHORTCUT_7"):
        row = rows[key]
        mapping = driver(session, row, "LENGTH")
        target = "hook:" + row["resolved"]["id"]["id"]
        frame = local_frame(session, target, frames["ribs_geom"]["world"])
        for axis in range(3):
            ref = reference(target, "transform", "position", component=axis)
            base, gain = value(session, ref), frame[axis * 4]
            expression = f"{base!r}*m + (value-{mapping['value']!r}*m)*{gain!r}"
            formula(session, mapping, ref, expression)
        result.append(mapping)
    return result


def basis(definitions):
    result = []
    rows = [d for d in definitions["drivers"] if d["owner"]["id"] == "hip_join_hook"]
    for row in sorted(rows, key=lambda d: d["array_index"]):
        text = row["driver"]["expression"]
        result.extend(
            float(re.search(r"([+-]?[0-9.eE]+)\*" + name, text)[1])
            for name in ("afx", "afy", "afz")
        )
        result.append(0.0)
    return (*result, 0.0, 0.0, 0.0, 1.0)


def hip_frame(session, definitions, frames):
    source = frames["hip_join_hook"]
    world = matrix(session.engine, frames[source["parent"]]["world"], source["parent_inverse"])
    frame = matrix(session.engine, world, basis(definitions))
    return local_frame(session, "hook:hip_join_hook", frame)


def hip_hook(session, rows, definitions, frames):
    mapping = driver(session, rows["SHORTCUT_105"], "LENGTH")
    secondary = [hidden(session, "Hip Joint Local " + name, dimension="LENGTH") for name in "YZ"]
    inputs = [
        dict(name=name, driver=item["driver"])
        for name, item in zip(("y", "z"), secondary, strict=True)
    ]
    frame = hip_frame(session, definitions, frames)
    for axis in range(3):
        ref = reference("hook:hip_join_hook", "transform", "position", component=axis)
        base = value(session, ref)
        a, b, c = frame[axis * 4 : axis * 4 + 3]
        expression = f"{base!r}*m+{a!r}*(value-{mapping['value']!r}*m)+{b!r}*y+{c!r}*z"
        formula(session, mapping, ref, expression, inputs)
    return mapping


def paired_bones(session):
    result = []
    for source, target, axis, scope in (
        ("SCP_14", "SCP_15", 0, "world_transform"),
        ("SCP_24", "SCP_25", 2, "transform"),
    ):
        mapping = hidden(session, session.document.entity(target).name + " length dependency")
        incoming = reference(source, scope, "scale", component=axis)
        ref = reference(target, "transform", "scale", component=axis)
        base, initial = value(session, ref), value(session, incoming)
        expression = f"{base!r} + (length-{initial!r})*{base / initial!r}"
        formula(session, mapping, ref, expression, [dict(name="length", property=incoming)])
        result.append(mapping)
    return result


def migrate(session, definitions, captured_frames):
    rows = {row["id"]: row for row in definitions["roots"]["AF_ROOT"]["shortcuts"]}
    frames = {row["name"]: row for row in captured_frames["objects"]}
    frames = {
        name: {
            key: tuple(v for row in data for v in row)
            if key in ("world", "local", "basis", "parent_inverse")
            else data
            for key, data in item.items()
        }
        for name, item in frames.items()
    }
    mappings = [*uniform_hooks(session, rows), *rib_hooks(session, rows, frames)]
    mappings.append(hip_hook(session, rows, definitions, frames))
    return mappings, paired_bones(session)
