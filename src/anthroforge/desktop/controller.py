from time import perf_counter as monotonic

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from anthroforge.application.session import Session
from anthroforge.native import scene
from anthroforge.profiling import RuntimeProfiler
from anthroforge.profiling.spans import measured

from . import controller_actions as actions
from . import presentation, project_actions, scene_projection, scene_state
from .activity_model import ActivityModel
from .inspection_export import InspectionExport
from .inspection_panel import InspectionPanel
from .issue_panel import IssuePanel
from .models import RenderModel


class Controller(QObject):
    changed = Signal()
    metricsChanged = Signal()
    selectionChanged = Signal()
    treeChanged = Signal()
    saveChoiceRequested = Signal(str)
    discardRequested = Signal(str)
    frameRequested = Signal(list)
    cameraRequested = Signal(list, bool)
    closeReady = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.initialize_session()
        self.activity_model = ActivityModel(self)
        self.render_model = RenderModel(self)
        self.render_model.activated.connect(self.activate_geometry)
        self._initialize_state()
        scene_projection.initialize(self)
        from .authoring import Authoring

        self.authoring = Authoring(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)
        self.refresh()

    def initialize_session(self):
        self.profiler = RuntimeProfiler()
        self.session = Session(profiler=self.profiler)
        scene.configure(self.session.engine)
        self.issue_panel = IssuePanel(self)
        self.inspection_panel = InspectionPanel(self)
        self.inspection_export = InspectionExport(self)

    def _initialize_state(self):
        self.selection, self.hovered, self.message = "", "", ""
        self.last_revision, self.last_workspace = -1, -1
        self.rows, self.drag_values, self.pick_ids = [], [], []
        self.pending_save, self.pending_document = "", None
        self.temporary_locks = []
        self.drag_mode = "Move"
        self.last_hit = {}
        self.tick_count = 0
        self.after_save = None
        self.camera_workspace = None
        self.capture_mode = False
        self.last_frame = monotonic()

    @Property(str, notify=changed)
    def documentName(self) -> str:
        return self.session.document.name

    @Property(str, notify=changed)
    def documentId(self) -> str:
        return str(self.session.document.id)

    @Property(QObject, constant=True)
    def meshModel(self):
        return self.render_model

    @Property("QVariantList", notify=treeChanged)
    def treeRows(self):
        return self.scene_projection.view.value("rows")

    @Property(QObject, constant=True)
    def selectedData(self):
        return self.scene_projection.selected

    @Property(QObject, constant=True)
    def sceneChoices(self):
        return self.scene_projection.view

    @Property(str, notify=selectionChanged)
    def selectedId(self):
        return self.selection

    @Property(str, notify=changed)
    def hoveredId(self):
        return self.hovered

    @Property(QObject, constant=True)
    def state(self):
        return self._state

    @Property(QObject, constant=True)
    def activityModel(self):
        return self.activity_model

    @Property(QObject, constant=True)
    def issuePanel(self):
        return self.issue_panel

    @Property(QObject, constant=True)
    def inspectionPanel(self):
        return self.inspection_panel

    @Property(QObject, constant=True)
    def inspectionExport(self):
        return self.inspection_export

    @Property("QVariantMap", notify=metricsChanged)
    def metrics(self):
        return self._metrics

    @measured("ui", lambda owner: owner.session.profiler)
    def notify(self):
        self._state.synchronize(self.snapshot())
        self.changed.emit()
        names = {row["id"]: row["name"] for row in self.rows}
        self.activity_model.synchronize(self.session.scheduler.jobs, names)
        self.refresh_metrics()
        self.issue_panel.synchronize()
        self.inspection_panel.synchronize()
        self.inspection_export.synchronize()

    def refresh_metrics(self):
        metrics = self.session.scheduler.metrics.report()
        if metrics != getattr(self, "_metrics", None):
            self._metrics = metrics
            self.metricsChanged.emit()

    def snapshot(self):
        return {
            **self.view_state(),
            "message": self.message,
            "revision": self.session.document.revision,
            "dirty": self.session.saved_revision != self.session.document.revision,
            "blocked": self.session.scheduler.blocked,
            "waiting": self.session.waiting_save,
            "publishing": len(self.render_model.pending),
            "path": str(self.session.path or ""),
        }

    def view_state(self):
        return {
            **presentation.state(self),
            "attachments": self.session.document.attachments_enabled,
            "mode": self.session.document.update_mode,
            "workspaces": [w.name for w in self.session.document.workspaces],
            "workspace": self.session.active_workspace,
            "hidden": list(self.session.workspace.hidden),
            "unpickable": list(self.session.workspace.unpickable),
            "handles": self.session.workspace.handles,
            "anchors": self.session.workspace.anchors,
            "diagnostics": self.session.workspace.diagnostics,
        }

    @Slot()
    def tick(self):
        started = monotonic()
        try:
            self.process_tick()
        except Exception as error:
            self.message = str(error)
            self.session.waiting_save = False
            self.notify()
        self.session.scheduler.metrics.observe("tick", monotonic() - started)

    @measured("ui", lambda owner: owner.session.profiler)
    def process_tick(self):
        self.session.scheduler.tick()
        project_actions.poll(self)
        self.render_model.drain()
        self.refresh_if_needed()
        self.issue_panel.synchronize()
        self.tick_count += 1
        if self.tick_count % 15 == 0:
            self.notify()

    @Slot()
    def frame_presented(self):
        now = monotonic()
        self.session.scheduler.metrics.observe("frame_interval", now - self.last_frame)
        self.last_frame = now
        self.render_model.presented()

    @measured("publication", lambda owner: owner.session.profiler)
    def activate_geometry(self):
        scene_state.picking_inputs(self, self.render_model.active_rows())
        from anthroforge.application.geometry_ownership import collect

        collect(self.session)
        self.notify()

    def refresh_if_needed(self):
        projection = self.scene_projection
        if (
            projection.session is not self.session
            or projection.cursor != self.session.changes.serial
            or self.last_workspace != self.session.active_workspace
        ):
            self.refresh()

    @measured("ui", lambda owner: owner.session.profiler)
    def refresh(self):
        scene_projection.refresh(self)
        self.last_revision = self.session.document.revision
        self.last_workspace = self.session.active_workspace
        self.notify()
        self.restore_camera()

    def restore_camera(self):
        identity = (str(self.session.document.id), self.session.active_workspace)
        if identity != self.camera_workspace:
            self.camera_workspace = identity
            self.cameraRequested.emit(
                list(self.session.workspace.camera), self.session.workspace.orthographic
            )

    @Slot("QVariantList", bool)
    def saveCamera(self, values, orthographic):
        if not self.session.waiting_save and not self.capture_mode:
            self.session.command("workspace.update", camera=values, orthographic=orthographic)

    @Slot(str)
    def afterSave(self, action):
        self.after_save = action

    @Slot(str, "QVariantMap", result="QVariant")
    def run(self, operation, arguments):
        return actions.run(self, operation, arguments)

    @Slot(str)
    def select(self, entity):
        self.selection = entity
        self.scene_projection.synchronize_selection()
        self.scene_projection.view.synchronize(
            dict(rows=self.rows, parents=self.scene_projection.parents())
        )
        self.authoring.refresh()
        self.notify()

    @Slot(str, float, str, bool)
    def importMesh(self, path, units, parent, y_up):
        result = self.run(
            "import",
            {"path": actions.local_path(path), "units": units, "parent": parent, "y_up": y_up},
        )
        if result:
            self.message = "Import queued. You can keep navigating and editing."

    @Slot("QVariantList", "QVariantList", int, bool, float, result="QVariantMap")
    def pick(self, origin, direction, depth, select, radius=0.03):
        self.last_hit = scene_state.picked(self, origin, direction, depth, radius)
        previous = self.hovered
        self.hovered = self.last_hit.get("id", "")
        if select:
            self.select(self.hovered)
        if select or previous != self.hovered:
            self.notify()
        return self.last_hit

    @Slot(str)
    def lockAnchor(self, mode):
        if self.last_hit.get("id") != self.selection:
            self.message = "Point at a face or vertex on the selected child SCP first."
            self.notify()
            return
        key = "face_lock" if mode == "FACE_CENTER" else "vertex_lock"
        index = self.last_hit["face" if key == "face_lock" else "vertex"]
        self.run("scp.attachment", {"entity": self.selection, "child_mode": mode, key: index})

    @Slot(str, result=bool)
    def beginTransform(self, mode):
        try:
            actions.start_transform(self, mode)
            return self.session.history.before is not None
        except Exception as error:
            self.message = str(error)
            self.notify()
            return False

    @Slot()
    @Slot(str)
    def rebaseTransform(self, mode=""):
        actions.rebase_transform(self, mode)

    @Slot(result="QVariantList")
    def selectionCenter(self):
        return actions.selection_center(self)

    @Slot("QVariantList", float, result="QVariantList")
    def rotationDelta(self, axis, angle):
        return [0, 0, 0, *scene.axis_rotation(self.session.engine, axis, angle), 1, 1, 1]

    @Slot(int, float)
    def dragTransform(self, axis, amount):
        actions.drag_transform(self, axis, amount)

    @Slot("QVariantList")
    def transformDelta(self, values):
        actions.transform_delta(self, values)

    @Slot(bool)
    def endTransform(self, cancel):
        actions.end_transform(self, cancel)

    @Slot()
    def frameSelection(self):
        actions.frame(self)

    @Slot(str, str)
    def saveProject(self, path, policy):
        try:
            project_actions.save(self, path, policy)
        except Exception as error:
            self.message = str(error)
            self.session.waiting_save = False
            self.notify()

    @Slot()
    def cancelSaveWait(self):
        for job in self.session.scheduler.active_jobs:
            if job.active and "@document" in job.outputs:
                self.session.scheduler.cancel_job(job.id)
        self.pending_save = ""
        self.after_save = None
        self.pending_document = None
        self.session.waiting_save = False
        self.notify()

    @Slot(str)
    def requestDocument(self, path):
        if self.session.document.revision != self.session.saved_revision:
            self.discardRequested.emit(path)
        else:
            self.replaceDocument(path)

    @Slot(str)
    def replaceDocument(self, path):
        project_actions.queue_document(self, path)

    @Slot()
    def newDocument(self) -> None:
        self.requestDocument("")

    def close(self):
        self.timer.stop()
        self.session.close()
        self.profiler.close()
        for lock in self.temporary_locks:
            lock.close()
