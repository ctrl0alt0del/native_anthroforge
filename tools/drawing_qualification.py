"""Serial headless fitting and cancellation evidence; no desktop or GPU interaction."""

import json
from pathlib import Path
from threading import Timer
from time import perf_counter

import numpy as np

from anthroforge.application.session import Session
from anthroforge.core.drawing import FitSettings
from anthroforge.native import drawing
from anthroforge.native.mesh import NativeCancellation

OUTPUT = Path("build/020-drawing-qualification")


def samples(count, frequency):
    x = np.linspace(0, 10, count)
    return np.column_stack((x, np.sin(x * frequency), x * 0))


def trial(session, count, frequency):
    points = samples(count, frequency)
    started = perf_counter()
    output = drawing.fit(session.engine, points, FitSettings())
    return dict(
        samples=count,
        frequency=frequency,
        authored_points=len(output),
        elapsed_ms=(perf_counter() - started) * 1000,
    )


def cancellation(session):
    token = NativeCancellation(session.engine)
    points = samples(100000, 1)
    timer = Timer(0.02, token.set)
    started = perf_counter()
    timer.start()
    try:
        drawing.fit(session.engine, points, FitSettings(), token.handle)
        raise AssertionError("Cancelled fitting output was returned")
    except ValueError as error:
        assert "cancel" in str(error), error
        return dict(request_after_ms=20, returned_after_ms=(perf_counter() - started) * 1000)
    finally:
        timer.join()


def measurements(session):
    rows = [
        trial(session, count, frequency)
        for count in (1000, 10000, 100000)
        for frequency in (1, 100)
    ]
    return dict(
        trials=rows,
        cancellation=cancellation(session),
        limit="Cancellation surrounds the atomic Blender fitting kernel",
    )


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    session = Session()
    try:
        session.command("profile.start")
        report = measurements(session)
        (OUTPUT / "measurements.json").write_text(json.dumps(report, indent=2))
        status = session.command(
            "profile.stop", path=str(OUTPUT / "drawing.afprofile.zip"), wait=True
        )
        assert status["state"] == "saved", status
        print(json.dumps(report, indent=2))
    finally:
        session.close()


if __name__ == "__main__":
    run()
