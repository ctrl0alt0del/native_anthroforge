"""Reproduce circle-object scale drivers without replacing source Bezier geometry."""

import json
import sys
from contextlib import closing
from pathlib import Path

from skeleton_shortcut_controls import driver, reference
from skeleton_shortcut_formulae import calibrated, consume_transforms, inputs, scaled_frame
from skeleton_shortcut_guides import settled
from skeleton_shortcut_hooks import hidden

from anthroforge.application.session import Session


def add_drivers(session, definitions, mappings):
    rows = {r["id"]: r for r in definitions["roots"]["AF_ROOT"]["shortcuts"]}
    for number in (1, 4, 5, 8, 10, 11, 12, 13, 14):
        key = "SHORTCUT_" + str(number)
        dimension = "ANGLE" if number in (10, 12, 13, 14) else "SCALAR"
        mappings[key] = driver(session, rows[key], dimension)


def rib_radii(session, mappings):
    for key, curve in (
        ("SHORTCUT_1", "ribs_curve"),
        ("SHORTCUT_4", "ribs_profile_top"),
        ("SHORTCUT_5", "ribs_profile_bottom"),
    ):
        consume_transforms(session, curve)
        ratio = f"radius/{mappings[key]['value']!r}"
        scaled_frame(
            session, curve, mappings[key], (ratio,) * 3, inputs(mappings, dict(radius=key))
        )
    sternum(session, mappings)


def sternum(session, mappings):
    mapping = hidden(session, "Sternum width dependency")
    incoming = inputs(mappings, dict(radius="SHORTCUT_1", angle="SHORTCUT_2"))
    calibrated(
        session,
        mapping,
        reference("SCP_3", "transform", "scale", component=1),
        "radius*sin(angle/2)",
        incoming,
    )
    return mapping


def pelvic_radii(session, mappings):
    radius, shrink = mappings["SHORTCUT_8"], mappings["SHORTCUT_11"]
    ratios = (
        f"radius/{radius['value']!r}",
        f"radius/{radius['value']!r}*shrink/{shrink['value']!r}",
        f"radius/{radius['value']!r}",
    )
    incoming = inputs(mappings, dict(radius="SHORTCUT_8", shrink="SHORTCUT_11"))
    for key in ("pelvic-guide",):
        consume_transforms(session, key)
        scaled_frame(session, key, radius, ratios, incoming)
    return ratios, incoming


def run(folder):
    definitions = json.loads((folder / "donor-definitions.json").read_text(encoding="utf-8"))
    saved = json.loads((folder / "migration.json").read_text(encoding="utf-8"))
    mappings = {m["source"]: m for m in saved["mappings"]}
    with closing(Session()) as session:
        session.command("open", path=str(folder / "guides-checkpoint.anthroforge"))
        settled(session)
        configure(session, definitions, mappings, folder)
        session.command(
            "save", path=str(folder / "radius-checkpoint.anthroforge"), blocked_policy="wait"
        )
    (folder / "radius-mapping.json").write_text(json.dumps(mappings, indent=2), encoding="utf-8")


def configure(session, definitions, mappings, folder):
    session.command("profile.start")
    try:
        session.begin()
        add_drivers(session, definitions, mappings)
        rib_radii(session, mappings)
        pelvic_radii(session, mappings)
        session.commit()
        settled(session)
        assert not session.scheduler.errors, session.scheduler.errors
    finally:
        session.command("profile.stop", path=str(folder / "radius.afprofile.zip"), wait=True)


if __name__ == "__main__":
    run(Path(sys.argv[1]))
