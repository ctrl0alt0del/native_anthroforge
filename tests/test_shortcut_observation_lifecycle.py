"""Causal observations survive retries and remain bounded without owning calculations."""

from anthroforge.core.jobs import Job
from tests.test_driving_formulas import curve, reference


def submitted(session, target, fail=False):
    def execute(value, cancel):
        if fail:
            raise ValueError("Fixture failure")
        return value

    job = Job("Observed fixture", frozenset({target}), lambda doc: 1, execute, lambda result: None)
    job.retry = lambda: submitted(session, target)
    session.scheduler.submit(job)
    return job


def test_retry_retains_edit_cause_and_clears_its_failure(session):
    target = curve(session)
    key = session.command("shortcut.expose", reference=reference(target))
    session.begin()
    session.command("shortcut.set", reference=reference(target), value=37)
    failed = submitted(session, target, fail=True)
    session.commit()
    session.wait(5)
    assert session.command("shortcut.progress", shortcut=key)["state"] == "failed"
    retried = session.scheduler.retry(failed.id)
    session.wait(5)
    assert retried.causes == failed.causes and retried.causes
    assert session.command("shortcut.progress", shortcut=key)["state"] == "complete"


def test_recent_edit_history_does_not_grow_with_each_gesture(session):
    keys = [session.command("driver.create") for _ in range(70)]
    for key in keys:
        session.command("driver.value", driver=key, value=1)
    session.wait(5)
    observer = session.shortcut_observation
    assert len(observer.latest) <= 64 and len(observer.effects) <= 8
    session.command("driver.value", driver=keys[0], value=2)
    session.wait(5)
    assert keys[0] in observer.latest and len(observer.records) <= 65


def test_readonly_jobs_do_not_become_shortcut_work(session):
    target = curve(session)
    key = session.command("shortcut.expose", reference=reference(target))
    session.begin()
    session.command("shortcut.set", reference=reference(target), value=37)
    job = readonly_job()
    session.scheduler.submit(job)
    session.commit()
    session.wait(5)
    assert not job.causes
    assert session.command("shortcut.progress", shortcut=key)["state"] == "complete"


def readonly_job():
    return Job(
        "Inspection",
        frozenset(),
        lambda doc: 1,
        lambda value, cancel: value,
        lambda result: None,
        writes=False,
    )
