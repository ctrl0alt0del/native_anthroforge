"""Large root graphs must distinguish valid ambiguity from an exhausted search."""

from collections import Counter
from itertools import product
from random import Random

import pytest

from anthroforge.application import surface_grouping
from anthroforge.application.surface_root_matching import allocate
from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.junctions import Junction, PointRef


def boundary(count, prefix):
    return Curve(
        tuple(
            CurvePoint(position=(i, 0, 0), junction=f"{prefix}{i}" if 0 < i < count - 1 else "")
            for i in range(count)
        )
    )


def crossed(session, count, distinct=True):
    first, second = boundary(3, "a"), boundary(count + 2 if distinct else 3, "b")
    children = [
        Curve(
            (
                CurvePoint(position=(0, 0, 0), junction="a1"),
                CurvePoint(position=(1, 0, 0), junction=f"b{i + 1}" if distinct else "b1"),
            )
        )
        for i in range(count)
    ]
    session.replace_document(objects=(first, second, *children), junctions=junctions(first, second))
    return [first.id, second.id, *(item.id for item in children)]


def junctions(first, second):
    return tuple(
        Junction(PointRef(item.id, point.id), point.junction)
        for item in (first, second)
        for point in item.points
        if point.junction
    )


def test_large_cross_connections_return_a_valid_suggested_group(session):
    curves = crossed(session, 30)
    result = session.command("surface.grouping", curves=curves)
    assert result["ambiguous"]
    surface_grouping.checked(session.document.registry.records, curves, result["plan"])
    assert all(group["boundary"] == curves[1] for group in result["plan"]["branches"])


def test_impossible_large_graph_is_rejected_instead_of_asking_about_invalid_groups(session):
    curves = crossed(session, 30, distinct=False)
    with pytest.raises(ValueError, match="distinct interior"):
        session.command("surface.grouping", curves=curves)


def feasible(values):
    return len(set(values)) == len(values) and 1 not in Counter(root[0] for root in values).values()


def test_root_allocation_matches_exhaustive_small_graphs():
    rng = Random(81)
    for _ in range(120):
        options = {
            str(i): [(side, rng.randrange(7)) for side in ("a", "b") if rng.random() > 0.2]
            for i in range(7)
        }
        expected = any(feasible(values) for values in product(*options.values()))
        result = allocate(options)
        assert (result is not None) == expected
        if result is not None:
            assert feasible(list(result.values()))
            assert all(slot in options[key] for key, slot in result.items())
