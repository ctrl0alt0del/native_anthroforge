from threading import Event

import pytest

from anthroforge.application import assembly_candidate, assembly_source, storage
from tests.test_assembly_mapping import prepared
from tests.test_assembly_repair import resolve
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


def test_repaired_input_resumes_without_enabling_external_writes(session, tmp_path):
    source, first, other, key, formula, outgoing = formula_source(session, tmp_path)
    candidate = prepared(session, source, [first])
    imported(session, candidate)
    references = session.document.external_references
    resolve(session, {r.id: dict(action="map", target=other) for r in references})
    session.wait()
    copied = session.document.formula_index.drivers[candidate.identities[key]]
    incoming = formula_result(session, candidate.identities[formula])
    assert incoming.status == "ready", incoming.error
    assert not next(f for f in copied.formulas if f.id == candidate.identities[outgoing]).enabled
    session.command("driver.value", driver=copied.id, value=3)
    session.wait()
    assert session.document.object(candidate.identities[first]).resolution == 5


def formula_result(session, key):
    return next(r for r in session.document.formula_results if r.formula == key)


def test_mapping_a_different_input_value_reevaluates_only_valid_internal_outputs(session, tmp_path):
    source, first, other, _, formula, outgoing = formula_source(session, tmp_path)
    destination = curve(session, "Different input")
    session.command("property.set", reference=reference(destination), value=7)
    candidate = prepared(session, source, [first], dict(mappings={other: destination}))
    assert candidate_result(candidate, formula).status == "pending"
    imported(session, candidate)
    assert session.document.object(candidate.identities[first]).resolution == 9
    assert session.document.object(destination).resolution == 7
    assert candidate.identities[outgoing] not in session.document.formula_index.formulas


def candidate_result(candidate, formula):
    return next(
        r
        for r in candidate.additions["formula_results"]
        if r.formula == candidate.identities[formula]
    )
