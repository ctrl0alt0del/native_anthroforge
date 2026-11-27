"""Read-only requested mode, execution phase and readiness for every client."""

from typing import Any

from . import skin_assessment
from . import skin_builder_configuration as builders

STAGES = dict(
    envelope="Draft",
    construction="skin pipeline",
    deformation="final skin",
    downstream="final skin",
)
PHASES = dict(
    restored="Saved state",
    waiting="Waiting for required inputs",
    failed="Skin update failed",
    blocked="Skin update blocked",
    current="Requested skin is current",
    empty="No contributing anatomy",
)


def describe(session: Any) -> dict[str, Any]:
    runtime = session.skin_pipeline
    jobs = runtime.active()
    state = readiness(session)
    current_phase = "empty" if not jobs and state["sources"] == "empty" else phase(runtime, jobs)
    stage = jobs[0].kind.removeprefix("skin_") if jobs else ""
    return state | dict(
        mode=session.document.skin.update_mode,
        phase=current_phase,
        stage=stage,
        reason=runtime.reason,
        can_retry=not jobs and current_phase in ("failed", "blocked"),
        label=label(current_phase, stage),
    )


def readiness(session: Any) -> dict[str, Any]:
    config = builders.automatic(session.document.skin)
    state = skin_assessment.assess(builders.projected(session.document, config), session.resources)
    return {
        name: getattr(state, name).condition
        for name in ("sources", "draft", "topology", "reference")
    }


def phase(runtime: Any, jobs: Any) -> str:
    if jobs:
        return "running" if jobs[0].state == "running" else "queued"
    if runtime.failed_stage and not runtime.desired:
        return "failed"
    if not runtime.armed:
        return "restored"
    if runtime.desired:
        return "waiting"
    return "blocked" if runtime.reason else "current"


def label(phase: str, stage: str) -> str:
    if stage:
        return ("Building " if phase == "running" else "Queued: ") + STAGES.get(stage, stage)
    return PHASES[phase]
