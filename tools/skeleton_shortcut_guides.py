"""Keep four source Bezier knots and their consumer frames in Parametric guides."""

import json
import sys
from contextlib import closing
from pathlib import Path
from time import monotonic

from anthroforge.application.session import Session

GUIDES = (
    "ribs_profile_bottom",
    "ribs_curve",
    "ribs_profile_middle1",
    "ribs_profile_top",
    "pelvic-guide",
    "pelvic-guide:mirror",
)


def polynomial(values):
    terms = []
    for index, value in enumerate(values):
        if value == 0:
            continue
        basis = "*".join(f"(t-{i})/({index}-{i})" for i in range(len(values)) if i != index)
        terms.append(f"({value!r}*m)*({basis})")
    return "+".join(terms) or "0*m"


def definition(curve):
    return dict(
        **{axis: polynomial([p.position[i] for p in curve.points]) for i, axis in enumerate("xyz")},
        resolution=len(curve.points),
        interpolation="BEZIER",
        bezier_resolution=curve.resolution,
        interval=dict(start=0.0, end=float(len(curve.points))),
    )


def convert(session):
    records = []
    session.begin()
    for key in GUIDES:
        curve = session.document.object(key)
        settings = definition(curve)
        session.command("curve.engine", curve=key, engine="PARAMETRIC", settings=settings)
        records.append(dict(curve=key, settings=settings))
    session.commit()
    settled(session)
    assert not session.scheduler.errors, session.scheduler.errors
    return records


def settled(session):
    deadline = monotonic() + 600
    while monotonic() < deadline:
        try:
            session.wait(30)
            return
        except TimeoutError:
            active = session.scheduler.active_jobs
            print([(j.label, j.state, j.progress) for j in active[:8]], flush=True)
    raise TimeoutError("Migration calculations did not settle within 600 seconds.")


def run(folder):
    with closing(Session()) as session:
        session.command("open", path=str(folder / "hooks-checkpoint.anthroforge"))
        session.wait(120)
        session.command("profile.start")
        try:
            records = convert(session)
        finally:
            session.command(
                "profile.stop", path=str(folder / "guide-conversion.afprofile.zip"), wait=True
            )
        session.command(
            "save", path=str(folder / "guides-checkpoint.anthroforge"), blocked_policy="wait"
        )
    (folder / "parametric-guides.json").write_text(json.dumps(records, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run(Path(sys.argv[1]))
