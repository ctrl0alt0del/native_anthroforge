"""Read-only job presentation; scheduler objects remain owned by the application."""


def job_row(job, names, now):
    return dict(
        jobId=job.id,
        label=job.label,
        jobState=job.state,
        error=job.error,
        progress=job.progress,
        elapsed=round((job.finished or now) - (job.started or job.created), 2),
        targets=", ".join(names.get(key) or "Project" for key in sorted(job.outputs)),
        retryable=job.retryable,
        cancellable=job.active,
        scheduling=scheduling_text(job),
    )


def scheduling_text(job):
    if job.assessment is None:
        return ""
    plan = job.assessment.schedule
    execution = job.execution or plan.execution
    estimate = "unmeasured" if plan.estimated_ms is None else f"{plan.estimated_ms:.2f} ms"
    actual = job.prepare_ms + job.compute_ms + job.publish_ms
    mode = "Immediate" if execution == "inline" else "Background"
    return (
        f"{mode} · planned wait {plan.delay_ms:.0f} ms · estimate {estimate}"
        f" · actual {actual:.2f} ms"
    )
