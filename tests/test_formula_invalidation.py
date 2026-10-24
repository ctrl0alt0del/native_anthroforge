"""Conservative reverse reads preserve full-scan invalidation semantics."""

from dataclasses import replace

from anthroforge.application import formula_observation
from tests.test_driving_formulas import curve, driver, reference, result


def test_unrelated_output_does_not_read_formula_sources(session, monkeypatch):
    target, unrelated = curve(session), curve(session)
    _, formula = driver(session, target, "8")
    session.wait(5)
    calls, original = [], formula_observation.source
    monkeypatch.setattr(
        formula_observation, "source", lambda *args: calls.append(args) or original(*args)
    )
    item = session.document.object(unrelated)
    updated = replace(item, result=replace(item.result, revision=item.result.revision + 1))
    session.replace_document(
        objects=tuple(updated if o.id == unrelated else o for o in session.document.objects)
    )
    assert not calls
    assert result(session, formula).status == "ready"


def test_changed_owner_reaches_formula_chain_and_restores_on_undo(session):
    first, second, third = curve(session), curve(session), curve(session)
    key, _ = driver(session, first, "value", value=8, kind="INTEGER")
    driver(session, second, "n+1", inputs=[dict(name="n", property=reference(first))])
    driver(session, third, "n+1", inputs=[dict(name="n", property=reference(second))])
    session.wait(5)
    session.command("driver.value", driver=key, value=12)
    session.wait(5)
    assert session.document.object(third).resolution == 14
    session.command("undo")
    session.wait(5)
    assert session.document.object(third).resolution == 10
