"""Read-only formula indexes share snapshot lifetimes, never mutable global state."""

from dataclasses import replace

import pytest

from anthroforge.application.formula_inputs import revision
from anthroforge.core.results import Port
from tests.test_driving_formulas import curve, driver


def test_index_reuses_definitions_but_observes_publication_and_undo(session):
    target = curve(session)
    key, formula = driver(session, target, "value", value=8, kind="INTEGER")
    session.wait(5)
    before = session.document
    assert replace(before, name="Renamed").formula_index is before.formula_index
    session.command("driver.value", driver=key, value=10)
    session.wait(5)
    after = session.document
    assert revision(before, Port(formula, "formula")) != revision(after, Port(formula, "formula"))
    assert before.formula_index.drivers[key].value == 8
    assert after.formula_index.drivers[key].value == 10
    session.command("undo")
    session.wait(5)
    assert session.document.formula_index.drivers[key].value == 8


def test_result_publication_reuses_immutable_authored_maps(session):
    target = curve(session)
    _, formula = driver(session, target, "8")
    session.wait(5)
    before = session.document
    results = tuple(replace(r, revision=r.revision + 1) for r in before.formula_results)
    after = replace(before, formula_results=results)
    assert after.formula_index.formulas is before.formula_index.formulas
    assert (
        after.formula_index.results[formula].revision
        == before.formula_index.results[formula].revision + 1
    )
    with pytest.raises(TypeError):
        after.formula_index.formulas[formula] = None
