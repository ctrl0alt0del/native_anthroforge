from threading import Event

import pytest

from anthroforge.application import assembly_candidate, assembly_source, storage
from tests.test_assembly_mapping import prepared
from tests.test_driving_formulas import curve, driver, reference


def formula_source(session, tmp_path):
    first, other = curve(session), curve(session, "External")
    inputs = [dict(name="x", property=reference(other))]
    key, formula = driver(session, first, "x + value", value=2, kind="INTEGER", inputs=inputs)
    outgoing = session.command(
        "driver.formula.add", driver=key, target=reference(other), expression="value"
    )
    session.wait()
    path = tmp_path / "formulas.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    source = assembly_source.inspect(str(path), Event())
    return source, first, other, key, formula, outgoing


def imported(session, candidate):
    session.begin()
    assembly_candidate.install(session, candidate)
    session.commit()
    session.wait()


def test_external_driver_output_stays_disabled_and_missing_input_blocks_only_reader(
    session, tmp_path
):
    source, first, other, key, formula, outgoing = formula_source(session, tmp_path)
    candidate = prepared(session, source, [first])
    imported(session, candidate)
    driver_id = candidate.identities[key]
    copied = session.document.formula_index.drivers[driver_id]
    assert not next(f for f in copied.formulas if f.id == candidate.identities[outgoing]).enabled
    session.command("driver.value", driver=driver_id, value=3)
    session.wait()
    assert any("Resolve imported" in job.error for job in session.scheduler.jobs)
    assert session.document.object(other).resolution == 2


def test_mapped_external_output_cannot_overwrite_destination_writer(session, tmp_path):
    source, first, other, key, _, outgoing = formula_source(session, tmp_path)
    candidate = prepared(session, source, [first], dict(mappings={other: other}))
    imported(session, candidate)
    copied = session.document.formula_index.drivers[candidate.identities[key]]
    formula = next(f for f in copied.formulas if f.id == candidate.identities[outgoing])
    assert not formula.enabled
    with pytest.raises(ValueError, match="one active formula"):
        session.command(
            "driver.formula.update",
            driver=copied.id,
            formula=formula.id,
            changes=dict(enabled=True),
        )
