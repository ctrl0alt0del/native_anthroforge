"""Active native objective and checkpoint settings retain routing safety and ABI defaults."""

from dataclasses import replace

import numpy as np
import pytest

from anthroforge.core.curve_engines import RoutingSettings, decode
from anthroforge.native import routing, routing_trace
from tests.routing_backend_cases import all_cases, inputs
from tests.test_routing_backends import quality


@pytest.mark.parametrize("backend", ["CUSTOM", "PIQP"])
def test_checkpoint_quantum_changes_boundaries_without_changing_route(session, backend):
    meshes, spec = fixture(session, backend)
    path, report = routing.evaluate(session.engine, spec)
    changed = settings(spec, checkpoint_steps=4)
    output, result = routing.evaluate(session.engine, changed)
    np.testing.assert_array_equal(output.array(), path.array())
    assert result.counters == report.counters
    assert 0 < result.measures[5] < report.measures[5]
    assert quality(session.engine, output, changed, case())["clear"]
    evidence = routing_trace.inspect(session.engine, changed)
    assert evidence["success"] and evidence["measures"][5] == report.measures[5]


@pytest.mark.parametrize("backend", ["CUSTOM", "PIQP"])
def test_length_weight_changes_objective_for_both_backends(session, backend):
    meshes, spec = fixture(session, backend)
    default, report = routing.evaluate(session.engine, spec)
    changed = settings(spec, length_weight=0)
    output, result = routing.evaluate(session.engine, changed)
    assert quality(session.engine, output, changed, case())["clear"]
    assert not np.allclose(output.array(), default.array())
    assert result.measures[0] < report.measures[0]


def case():
    return next(row for row in all_cases() if row["name"] == "snapped_cube-128-fiber")


def fixture(session, backend):
    meshes, spec = inputs(session.engine, case())
    return meshes, replace(spec, backend=backend)


def settings(spec, **values):
    return replace(
        spec,
        curve=replace(spec.curve, engine_settings=replace(spec.curve.engine_settings, **values)),
    )


@pytest.mark.parametrize(
    "values",
    [
        dict(length_weight=-1),
        dict(length_weight=float("nan")),
        dict(checkpoint_steps=0),
        dict(checkpoint_steps=1.5),
    ],
)
def test_invalid_execution_settings_are_rejected(values):
    with pytest.raises(ValueError):
        RoutingSettings(**values)


def test_saved_execution_settings_decode_and_old_settings_keep_defaults():
    assert decode("ROUTED", dict(length_weight=2.5, checkpoint_steps=4)) == RoutingSettings(
        length_weight=2.5, checkpoint_steps=4
    )
    assert decode("ROUTED").length_weight == 0.9
    assert decode("ROUTED").checkpoint_steps == 1
