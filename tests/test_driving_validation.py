"""Independent candidate failures and real construction/property lifecycle integration."""

from anthroforge.application import storage
from tests.test_driving_formulas import curve, driver, reference, result
from tests.test_tissue_workflow import assembly


def inflation_reference(target, field):
    return reference(target, ("parts", "@main", "a", "inflation", field))


def test_conflicting_tissue_limits_retain_group_but_apply_independent_power(session):
    _, _, target = assembly(session)
    original = session.document.object(target).parts[0].a.inflation
    _, low = driver(session, target, "0.015*m", path=inflation_reference(target, "minimum"))
    _, high = driver(session, target, "0.01*m", path=inflation_reference(target, "amount"))
    _, power = driver(session, target, "3.0", path=inflation_reference(target, "power"))
    session.wait(10)
    final = session.document.object(target).parts[0].a.inflation
    assert (final.minimum, final.amount) == (original.minimum, original.amount)
    assert final.power == 3.0
    assert result(session, low).status == result(session, high).status == "failed"
    assert result(session, power).status == "ready"


def test_valid_joint_tissue_limits_do_not_validate_intermediates(session):
    _, _, target = assembly(session)
    _, low = driver(session, target, "0.03*m", path=inflation_reference(target, "minimum"))
    _, high = driver(session, target, "0.04*m", path=inflation_reference(target, "amount"))
    session.wait(10)
    assert result(session, low).status == result(session, high).status == "ready"
    final = session.document.object(target).parts[0].a.inflation
    assert (final.minimum, final.amount) == (0.03, 0.04)


def test_invalid_expression_is_authored_and_can_recover(session):
    target = curve(session)
    key, formula = driver(session, target, "")
    session.wait(5)
    assert result(session, formula).status == "failed"
    assert session.document.object(target).resolution == 24
    session.command(
        "driver.formula.update", driver=key, formula=formula, changes=dict(expression="9")
    )
    session.wait(5)
    assert result(session, formula).status == "ready"
    assert session.document.object(target).resolution == 9


def test_results_roundtrip_with_complete_read_set(session):
    target = curve(session)
    _, formula = driver(session, target, "8")
    session.wait(5)
    assert result(session, formula).inputs
    assert storage.decode_document(storage.document_state(session.document)) == session.document


def test_referenced_property_cannot_disappear_without_resolving_formula(session):
    import pytest

    target = curve(session)
    _, formula = driver(session, target, "8")
    session.wait(5)
    with pytest.raises(ValueError, match="Resolve driving shortcut"):
        session.command("object.delete", target=target)
    assert session.document.object(target).resolution == 8
    assert result(session, formula).status == "ready"
