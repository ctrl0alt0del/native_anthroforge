"""Provider isolation, evidence identity, stale checks and honest coverage."""

from dataclasses import replace

import pytest

from anthroforge.application.issues.presentation import Presentation
from anthroforge.application.issues.reporting import Reporting
from anthroforge.application.issues.repository import IssueRepository
from anthroforge.application.issues.resolution import Resolution, Solver
from anthroforge.core.issues import Issue, evidence


@pytest.fixture
def reporting():
    return Reporting(IssueRepository())


def issue(provider="test.v1", source="one"):
    return Issue(provider, "target", "DEFECT", "Measured problem", target="target", source=source)


def test_providers_reconcile_without_clearing_other_evidence(reporting):
    first, second = issue(), issue("other.v1")
    reporting.report(first)
    reporting.report(second)
    reporting.complete(reporting.begin(first.provider, first.scope), ())
    assert set(reporting.repository.records) == {second.id}


def test_obsolete_and_previous_document_checks_cannot_publish(reporting):
    old = reporting.begin("test.v1", "target")
    current = reporting.begin("test.v1", "target")
    assert reporting.complete(current, (issue(),))
    assert not reporting.complete(old, ())
    reporting.reset()
    assert not reporting.complete(current, (issue(),))
    assert not reporting.repository.records


def test_failed_and_cancelled_checks_keep_stale_evidence(reporting):
    reporting.report(issue())
    view = Presentation(reporting.repository)
    check = reporting.begin("test.v1", "target")
    reporting.fail(check, "Worker unavailable")
    assert view.get(issue().id)["freshness"] == "stale"
    assert not view.status()["complete"] and not view.status()["clean"]
    reporting.fail(reporting.begin("test.v1", "target"), "Cancelled", True)
    assert view.get(issue().id)["check_state"] == "CANCELLED"


def test_dismissal_is_revision_specific_and_does_not_certify_clean(reporting):
    reporting.report(issue())
    reporting.repository.dismiss(issue().id)
    view = Presentation(reporting.repository)
    assert view.query()["total"] == 0 and not view.status()["clean"]
    assert view.query(include_dismissed=True)["total"] == 1
    new = issue(source="two")
    reporting.complete(reporting.begin(new.provider, new.scope), (new,))
    assert view.query()["records"][0]["id"] == new.id


def test_evidence_snapshot_and_filters_are_read_only(reporting):
    values = {"faces": [1, 2]}
    row = replace(issue(), evidence=evidence(details=values), stage="surface", severity="error")
    values["faces"].append(3)
    reporting.report(row)
    view = Presentation(reporting.repository)
    result = view.query(filters={"stage": "surface", "severity": "error"})
    assert result["records"][0]["evidence"]["details"]["faces"] == [1, 2]
    with pytest.raises(ValueError, match="filter"):
        view.query(filters={"typo": "anything"})


def test_repair_is_explicit_fresh_and_requires_verification(reporting):
    called = []
    resolution = Resolution(reporting.repository, lambda name: reporting.begin(name, "target"))
    resolution.register(
        Solver("fix", "Fix", ("DEFECT",), lambda _: True, lambda _: called.append(1) or ())
    )
    reporting.report(issue())
    Presentation(reporting.repository).query()
    assert not called
    repair = resolution.invoke(issue().id, "fix")
    resolution.verify(repair)
    assert repair.state == "VERIFYING"
    reporting.complete(reporting.begin("test.v1", "target"), ())
    resolution.verified(repair)
    assert repair.state == "DONE" and called == [1]


def test_scope_mismatch_does_not_remove_accepted_evidence(reporting):
    reporting.report(issue())
    check = reporting.begin("test.v1", "target")
    with pytest.raises(ValueError, match="own provider"):
        reporting.complete(check, (issue("other.v1"),))
    assert issue().id in reporting.repository.records
