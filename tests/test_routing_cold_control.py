"""An authoritative cold route bypasses reuse without changing authored warm-start policy."""

import pytest

from anthroforge.native import routing
from tests.test_fiber_creation import bind, scene


def observe(monkeypatch):
    values, original = [], routing.evaluate

    def capture(engine, inputs, cancel=0):
        values.append(inputs.warm)
        return original(engine, inputs, cancel)

    monkeypatch.setattr(routing, "evaluate", capture)
    return values


def routed(session, fiber):
    target, curve = scene(session)
    curve = bind(session, target, curve).id if fiber else curve
    session.command("curve.engine", curve=curve, engine="ROUTED")
    session.wait()
    return curve


@pytest.mark.parametrize("fiber", [False, True])
def test_cold_recalculate_publishes_and_normal_reuse_remains(session, monkeypatch, fiber):
    curve = routed(session, fiber)
    values = observe(monkeypatch)
    session.command("evaluate", entities=[curve])
    session.wait()
    assert values[-1] is not None
    previous = session.document.object(curve).result.asset
    session.command("curve.reroute", curve=curve)
    session.wait()
    current = session.document.object(curve)
    assert values[-1] is None and current.result.asset != previous
    assert current.engine_settings.use_warm_start and not session.scheduler.errors


def test_disabling_warm_start_persists_and_routes_cold(session, monkeypatch, tmp_path):
    curve = routed(session, False)
    values = observe(monkeypatch)
    session.command("curve.engine_settings", curve=curve, use_warm_start=False)
    session.wait()
    assert values[-1] is None
    session.command("evaluate", entities=[curve])
    session.wait()
    assert values[-1] is None
    path = tmp_path / "cold.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    session.command("open", path=str(path))
    assert not session.document.object(curve).engine_settings.use_warm_start
