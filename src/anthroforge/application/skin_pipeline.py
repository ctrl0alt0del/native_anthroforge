"""One skin-domain planner, using the existing coordinator for every execution."""

from dataclasses import replace
from typing import Any

from anthroforge.core import skin_sources
from anthroforge.core.results import Port
from anthroforge.core.skin_pipeline import Condition, plan

from . import (
    skin_assessment,
    skin_inputs,
    skin_job_intents,
    skin_jobs,
    skin_stages,
    skin_state_inputs,
    skin_update_tasks,
)
from . import skin_builder_configuration as builders
from .construction_policy import revisions
from .service_lifecycle import Event, Service

KINDS = frozenset("skin_" + stage for stage in (*skin_stages.POLICIES, "deformation"))


def attach(session: Any) -> Service:
    session.skin_pipeline = Pipeline(session)
    runtime = session.skin_pipeline
    return Service(
        "skin_pipeline",
        (
            (Event.DOCUMENT_CHANGED, runtime.changed),
            (Event.SYNCHRONIZE, runtime.synchronize),
            (Event.GESTURE_BEGIN, runtime.begin),
            (Event.GESTURE_COMMITTED, runtime.committed),
            (Event.HISTORY_RESTORED, runtime.restored),
            (Event.CLOSE, runtime.close),
        ),
    )


def anatomy_key(document: Any) -> Any:
    document = builders.projected(document, builders.automatic(document.skin))
    sources = skin_sources.contributors(document)
    ports = set().union(*(skin_inputs.source_ports(row) for row in sources))
    ports |= {Port(row.owner, "base") for row in sources if row.kind == "TISSUE"}
    return sources, revisions(document, ports), builder_key(document)


def builder_key(document: Any) -> Any:
    from .skin_builder_registry import BUILDERS

    builder = BUILDERS.get(document.skin.draft_settings.backend)
    return builder.signature(document) if builder else ()


class Pipeline:
    def __init__(self, session: Any) -> None:
        self.session, self.epoch = session, 0
        self.armed = self.desired = self.transition = self.manual = False
        self.handoff = False
        self.dirty = True
        self.pending_config: Any = None
        self.retry_config: Any = None
        self.repair = self.failed_stage = ""
        self.attempted_repairs: set[str] = set()
        self.repair_key: Any = None
        self.last_key = anatomy_key(session.document)
        self.before = session.document
        self.previous_jobs: set[str] = set()
        self.reason = ""
        self.observed_inputs = skin_state_inputs.key(session.document)

    def changed(self) -> None:
        current = skin_state_inputs.key(self.session.document)
        self.dirty |= current != self.observed_inputs
        self.observed_inputs = current

    def begin(self) -> None:
        self.before = self.session.document
        self.previous_jobs = {job.id for job in self.session.scheduler.active_jobs}

    def committed(self) -> None:
        if self.session._editing.key:
            return
        current = self.session.document
        changed = anatomy_key(current) != anatomy_key(self.before)
        self.armed |= changed or self.new_source_work()
        self.desired |= changed
        if not self.manual:
            self.committed_target(current)
        self.manual = False
        self.synchronize()

    def new_source_work(self) -> bool:
        return any(
            j.id not in self.previous_jobs and j.writes and j.kind not in KINDS
            for j in self.session.scheduler.active_jobs
        )

    def committed_target(self, current: Any) -> None:
        if current.skin.draft_settings.backend != self.before.skin.draft_settings.backend:
            self.invalidate()
            self.pending_config = current.skin.draft_settings.configuration()
            self.repair, self.desired, self.armed = "envelope", True, True
        if current.skin.update_mode != self.before.skin.update_mode:
            self.handoff = current.skin.update_mode == "FINAL"
            if current.skin.update_mode == "DRAFT":
                self.invalidate()
            self.desired = self.transition = self.armed = True
        if current.skin.deformation_settings != self.before.skin.deformation_settings:
            self.desired |= current.skin.update_mode == "FINAL"

    def synchronize(self) -> None:
        session = self.session
        if session._editing.key or not self.dirty:
            return
        if session.history.before is not None and not self.live():
            return
        key = anatomy_key(session.document)
        self.desired |= self.armed and key != self.last_key
        self.last_key, self.dirty = key, False
        if self.desired and self.allowed() and not self.active():
            self.request()

    def live(self) -> bool:
        doc = self.session.document
        return bool(doc.skin.update_mode == "FINAL" and doc.update_mode == "LIVE")

    def allowed(self) -> bool:
        doc = self.session.document
        return doc.skin.update_mode == "DRAFT" or self.transition or doc.update_mode != "MANUAL"

    def active(self) -> tuple[Any, ...]:
        return tuple(j for j in self.session.scheduler.active_jobs if j.kind in KINDS)

    def request(self) -> None:
        config = self.pending_config or builders.automatic(self.session.document.skin)
        doc = builders.projected(self.session.document, config)
        state = self.session.skin_status.pipeline_inputs(config)
        planned = plan(doc.skin.update_mode, state, self.handoff)
        self.reason = planned.reason
        stage = self.repair or planned.stage
        if not self.ready(doc, state, stage):
            return
        self.repair = ""
        self.dispatch(stage, config)

    def ready(self, document: Any, state: Any, stage: str) -> bool:
        if state.sources.condition != Condition.READY or not stage:
            self.desired = state.sources.condition == Condition.WAITING
            return False
        if stage in ("envelope", "construction") and state.draft.condition == Condition.UNAVAILABLE:
            self.reason, self.desired = state.draft.reason, False
            return False
        required = skin_assessment.required(document, self.session.resources, stage)
        if required.condition != Condition.READY:
            self.reason = required.reason
            return False
        return True

    def dispatch(self, stage: str, config: Any) -> str:
        session = self.session
        if stage != "envelope":
            self.handoff = False
        intent = skin_job_intents.capture(session, stage, True, config)
        if stage == "deformation":
            return str(skin_update_tasks.request(session, interactive=self.live(), intent=intent))
        return str(skin_jobs.enqueue(session, stage, session.document.revision, intent))

    def completed(self, job: Any, intent: Any, state: str) -> None:
        self.dirty = True
        if intent.epoch != self.epoch:
            return
        if state in ("failed", "cancelled"):
            self.failed(job, intent)
        elif state == "succeeded":
            self.pending_config = None
            self.failed_stage, self.retry_config = "", None
            self.desired = intent.automatic
            if self.session.document.skin.update_mode == "DRAFT" or job.kind != "skin_envelope":
                self.transition = False

    def failed(self, job: Any, intent: Any) -> None:
        self.failed_stage = job.kind.removeprefix("skin_")
        self.retry_config = intent.configuration
        self.pending_config = None
        previous = anatomy_key(job.snapshot) if job.snapshot else self.last_key
        self.desired = previous != anatomy_key(self.session.document)
        self.transition = False
        self.reason = job.error or "Skin operation cancelled."

    def explicit(self, stage: str) -> None:
        self.invalidate()
        self.handoff = False
        self.manual, self.armed = True, True
        self.desired = self.transition = False
        if stage != "envelope":
            skin = self.session.document.skin
            self.session.replace_document(skin=replace(skin, update_mode="FINAL"))

    def retry(self) -> str:
        self.invalidate()
        self.pending_config = self.retry_config or builders.automatic(self.session.document.skin)
        self.repair = self.failed_stage
        self.desired = self.transition = self.armed = self.dirty = True
        self.request()
        return next((j.id for j in self.active()), "")

    def evaluate(self) -> str:
        self.desired = self.transition = self.armed = self.dirty = True
        skin = self.session.document.skin
        if skin.update_mode == "FINAL" and skin.reference:
            self.repair = "deformation"
        if not self.active():
            self.request()
        return next((j.id for j in self.active()), "")

    def resume(self, stage: str, configuration: Any) -> None:
        self.pending_config, self.repair = configuration, stage
        self.desired = self.armed = self.dirty = True
        self.synchronize()

    def invalidate(self) -> None:
        self.epoch += 1
        self.attempted_repairs.clear()
        for job in self.active():
            self.session.scheduler.cancel_job(job.id, obsolete=True, reason="skin_target_changed")

    def require_repair(self, stage: str, reason: str) -> None:
        if stage not in ("construction", "reference"):
            raise ValueError("Unsupported skin prerequisite repair stage: " + stage)
        key = anatomy_key(self.session.document), self.session.document.skin.deformation_settings
        if key != self.repair_key:
            self.attempted_repairs.clear()
        self.repair_key = key
        if stage in self.attempted_repairs:
            raise ValueError("Skin prerequisite repair made no progress: " + reason)
        self.attempted_repairs.add(stage)
        self.repair, self.reason = stage, reason

    def restored(self) -> None:
        self.invalidate()
        self.handoff = False
        self.pending_config, self.repair = None, ""
        self.last_key = anatomy_key(self.session.document)
        self.armed = self.desired = self.dirty = True
        self.transition = False

    def close(self) -> None:
        self.epoch += 1
        self.desired = self.armed = False
