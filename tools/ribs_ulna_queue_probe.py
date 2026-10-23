"""Diagnostic-only queue observations and an opt-in priority counterfactual."""

from time import perf_counter


def blockers(coordinator, job):
    return [
        dict(id=other.id, label=other.label, kind=other.kind)
        for other in coordinator.blockers(job)
        if other is not job
        and other.active
        and (
            other.provides & job.prerequisites
            or other.future is not None
            and other.outputs & job.outputs
        )
    ]


def snapshot(coordinator):
    jobs = coordinator.active_jobs
    waiting = [j for j in jobs if "SCP_15" in j.outputs and j.state == "queued"]
    return dict(
        targets=[
            dict(id=j.id, kind=j.kind, ready=j.ready_at, blockers=blockers(coordinator, j))
            for j in waiting
        ],
        running=[
            dict(id=j.id, kind=j.kind, done=j.future.done()) for j in jobs if j.future is not None
        ],
    )


def monitor(coordinator):
    output, previous = [], [None]
    original = coordinator.service_tick

    def tick():
        original()
        current = snapshot(coordinator)
        if current != previous[0]:
            output.append(dict(time=perf_counter(), **current))
            previous[0] = current

    coordinator.service_tick = tick
    return output


def prioritize(coordinator):
    original = coordinator.queued
    coordinator.queued = lambda: sorted(
        original(), key=lambda job: job.kind not in ("attachments", "formulas")
    )
