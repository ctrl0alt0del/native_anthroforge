"""Direct-stage adapter parity on a planner-trivial case and explicit endpoint constraints."""

from types import SimpleNamespace as NS

import numpy as np
import solver_only
from hybrid_retest import write

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import PolylineSettings, RoutingSettings
from anthroforge.native import paths, routing
from anthroforge.native.mesh import GeometryEngine


def fixture(engine):
    item = Curve(
        (CurvePoint(position=(-1, 0, 0)), CurvePoint(position=(1, 0, 0))),
        engine_settings=RoutingSettings(samples=73, accepted_steps=1),
    )
    seed = Curve(
        tuple(CurvePoint(position=(x, 0, 0)) for x in np.linspace(-1, 1, 73)),
        engine_settings=PolylineSettings(),
    )
    seed = NS(path=paths.evaluate(engine, seed))
    return item, seed


def run():
    engine = GeometryEngine()
    item, seed = fixture(engine)
    scene = solver_only.Scene(solver_only.library(), [], 0.002)
    actual = solver_only.evaluate(NS(engine=engine), item, seed, scene, (0, 0))
    expected, _ = routing.evaluate(engine, routing.Inputs(item))
    error = float(np.max(np.abs(actual.path.array() - expected.array())))
    assert actual.success and not actual.planner_used and error < 1e-10
    record(actual, error)


def record(actual, error):
    write(
        "qualification.json",
        dict(
            straight_path_parity=error,
            native_validated=actual.success,
            planner_used=False,
            production_solver_stage="routing_solve.cpp",
        ),
    )


if __name__ == "__main__":
    run()
