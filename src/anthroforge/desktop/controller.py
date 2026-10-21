from time import perf_counter as monotonic
from weakref import WeakMethod

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from anthroforge.application.session import Session
from anthroforge.native import scene
from anthroforge.profiling import RuntimeProfiler
from anthroforge.profiling.spans import measured

from . import controller_actions as actions
from . import presentation, project_actions, scene_projection, scene_state
from .activity_model import ActivityModel
from .creation_selection import CreationSelection
from .drawing_tools import DrawingTools
from .image_tools import ImageTools
from .inspection_export import InspectionExport
from .inspection_panel import InspectionPanel
from .inspection_tools import InspectionTools
from .issue_panel import IssuePanel
from .models import RenderModel
from .numeric_edits import NumericEdits
from .object_selection import ObjectSelection
from .route_inspection_tools import RouteInspectionTools
from .routing_choices import RoutingChoices
from .section_tools import SectionTools
from .surface_creation import SurfaceCreation
from .tissue_inspection_tools import TissueInspectionTools
from .tissue_painting_tools import TissuePaintingTools
from .tissue_region_tools import TissueRegionTools


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
        self.initialize_renderers()
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
        self.initialize_tools()
        self.profiler.resources.views[self] = WeakMethod(self.memory_owners)

    def initialize_tools(self):
        self.numeric_edits = NumericEdits(self)
        self.issue_panel = IssuePanel(self)
        self.inspection_panel = InspectionPanel(self)
        self.inspection_export = InspectionExport(self)
        self.inspection_tools = InspectionTools(self)
        self.image_tools = ImageTools(self)
        self.drawing_tools = DrawingTools(self)
        self.creation_selection = CreationSelection(self)
        self.routing_choices = RoutingChoices()
        self.initialize_tissue_tools()
        self.surface_creation = SurfaceCreation(self)

    def initialize_tissue_tools(self):
        self.tissue_region_tools = TissueRegionTools(self)
        self.tissue_inspection = TissueInspectionTools(self)
        self.tissue_painting = TissuePaintingTools(self)
        self.section_tools = SectionTools(self)
        self.route_inspection = RouteInspectionTools(self)

    def memory_owners(self, owners):
        for model in self.geometry_models():
            model.memory_owners(owners)
        owners["drawing_preview"].update(self.drawing_tools.leases)
        if self.drawing_tools.stroke is not None:
            owners["drawing_preview"].add(self.drawing_tools.stroke)
        if self.tissue_painting.preview:
            owners["drawing_preview"].add(self.tissue_painting.preview["resource"])

    def geometry_models(self):
        return self.render_model, self.path_model, self.image_model, self.tissue_inspection.model

    def initialize_renderers(self):
        from .image_scene import prepare_picking as prepare_images
        from .path_scene import prepare_picking

        self.render_model, self.path_model = RenderModel(self), RenderModel(self)
        self.image_model = RenderModel(self)
        self.initialize_image_layers()
        self.render_model.activated.connect(self.activate_geometry)
        self.path_model.activated.connect(self.activate_geometry)
        self.path_model.activated.connect(self.drawing_tools.branch.invalidate)
        self.image_model.activated.connect(self.activate_geometry)
        prepare_picking(self)
        prepare_images(self)

    def initialize_image_layers(self):
        from .render_layer import RenderLayer

        self.image_layers = {
            key: RenderLayer(self.image_model, key) for key in ("NORMAL", "FRONT", "BACK")
        }
        self.viewport_orthographic = False
        self.viewport_direction = (0, 0, 1)

    @Slot(bool)
    def setViewportProjection(self, orthographic):
        self.viewport_orthographic = orthographic

    @Slot(list)
    def setViewportDirection(self, direction):
        self.viewport_direction = tuple(direction)

    def _initialize_state(self):
        self.object_selection = ObjectSelection()
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

    @property
    def selection(self):
        return self.object_selection.primary

    @selection.setter
    def selection(self, value):
        self.object_selection.choose(value)

    @Property(str, notify=changed)
    def documentName(self) -> str:
        return self.session.document.name

    @Property(str, notify=changed)
    def documentId(self) -> str:
        return str(self.session.document.id)

    @Property(QObject, constant=True)
    def meshModel(self):
        return self.render_model

    @Property(QObject, constant=True)
    def pathModel(self):
        return self.path_model

    @Property("QVariantMap", notify=changed)
    def conversionState(self):
        from anthroforge.application.curve_conversion import status

        return status(self.session)

    def conversion_key(self):
        return tuple(
            (v.token, v.state, id(v.asset))
            for v in (
                self.session.conversion,
                self.session.surface_preview,
                self.session.tissue_preview,
            )
        )

    @Property("QVariantMap", notify=changed)
    def surfacePreview(self):
        from anthroforge.application.surface_preview import status

        return status(self.session)

    @Property("QVariantMap", notify=changed)
    def tissuePreview(self):
        from anthroforge.application.tissue_preview import status

        from .values import qml

        return qml(status(self.session))

    @Property(QObject, constant=True)
    def imageModel(self):
        return self.image_model

    @Slot(str, result=QObject)
    def imageLayer(self, depth):
        return self.image_layers[depth]

    @Property("QVariantList", notify=treeChanged)
    def treeRows(self):
        return self.scene_projection.view.value("rows")

    @Property(QObject, constant=True)
    def constructionModel(self):
        return self.construction.model

    @Property(QObject, constant=True)
    def selectedData(self):
        return self.scene_projection.selected

    @Property(QObject, constant=True)
    def sceneChoices(self):
        return self.scene_projection.view

    @Property(str, notify=selectionChanged)
    def selectedId(self):
        return self.selection

    @Property("QVariantList", notify=selectionChanged)
    def selectedObjects(self):
        return self.object_selection.items

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

    @Property(QObject, constant=True)
    def inspectionTools(self):
        return self.inspection_tools

    @Property(QObject, constant=True)
    def imageTools(self):
        return self.image_tools

    @Property(QObject, constant=True)
    def drawingTools(self):
        return self.drawing_tools

    @Property(QObject, constant=True)
    def tissueRegionTools(self):
        return self.tissue_region_tools

    @Property(QObject, constant=True)
    def tissueInspection(self):
        return self.tissue_inspection

    @Property(QObject, constant=True)
    def tissuePainting(self):
        return self.tissue_painting

    @Property(QObject, constant=True)
    def sectionTools(self):
        return self.section_tools

    @Property(QObject, constant=True)
    def routeInspection(self):
        return self.route_inspection

    @Slot()
    def cancelViewportTools(self, keep=None):
        tools = (
            self.inspection_tools,
            self.image_tools,
            self.drawing_tools,
            self.tissue_region_tools,
            self.tissue_inspection,
            self.tissue_painting,
        )
        for tool in tools:
            if tool is not keep:
                tool.cancel()

    @Slot(result="QVariantList")
    def ordinaryParents(self):
        from .image_tools import parent_choices

        return parent_choices(self)

    @Slot(str)
    def createSurface(self, kind):
        from .construction_creation import surface

        surface(self, kind)

    @Property(QObject, constant=True)
    def surfaceCreation(self):
        return self.surface_creation

    @Slot(str)
    def editConstruction(self, target):
        from .construction_navigation import edit

        edit(self, target)

    @Slot()
    def focusSelection(self):
        from .construction_navigation import focus

        focus(self)

    @Slot(result="QVariantList")
    def tissueSources(self):
        from .construction_navigation import tissue_sources

        return tissue_sources(self)

    @Slot()
    def createPoint(self):
        from .image_tools import context_owner

        target = self.run("construction.point.create", {"owner": context_owner(self)})
        if target:
            self.select(target)

    @Slot(result="QVariantList")
    def surfaceRoles(self):
        from .surface_choices import rows

        return rows(self)

    @Slot(result="QVariantList")
    def stackingTissues(self):
        from .tissue_projection import choices

        return choices(self)

    @Property("QVariantMap", notify=changed)
    def surfaceAction(self):
        from .construction_creation import surface_action

        return surface_action(self)

    @Slot(str, str, result="QVariantMap")
    def surfaceOptions(self, target, boundary):
        from .surface_tools import choices

        return choices(self, target, boundary)

    @Slot(result="QVariantList")
    def anatomicalSurfaces(self):
        from anthroforge.core.results import geometry_asset

        return [
            dict(id=item.id, name=item.name)
            for item in self.session.document.entities
            if geometry_asset(item)
        ]

    @Slot(QObject, result=QObject)
    def createChoiceModel(self, owner):
        from .choice_model import ChoiceModel

        return ChoiceModel(owner)

    @Slot(str, result="QVariantList")
    def conversionPoints(self, key):
        from .routing_choices import point_rows

        return point_rows(self.session.document, key)

    @Slot(str, "QVariantMap", result="QVariantList")
    def routingChoices(self, key, settings):
        return self.routing_choices.rows(self.session.document, key, settings)

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
        self.refresh_viewport_tools()

    def refresh_viewport_tools(self):
        self.inspection_tools.synchronize()
        self.image_tools.synchronize()
        self.drawing_tools.synchronize()
        self.tissue_region_tools.synchronize()
        self.tissue_painting.synchronize()
        self.tissue_inspection.synchronize()
        self.section_tools.synchronize()
        self.route_inspection.synchronize()

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
            "publishing": sum(len(m.pending) for m in self.geometry_models()),
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
        for model in self.geometry_models():
            model.drain()
        self.tissue_painting.synchronize()
        self.tissue_inspection.synchronize()
        self.refresh_if_needed()
        self.section_tools.synchronize()
        self.route_inspection.synchronize()
        self.creation_selection.synchronize()
        self.issue_panel.synchronize()
        self.tick_count += 1
        if self.tick_count % 15 == 0:
            self.notify()

    @Slot()
    def frame_presented(self):
        now = monotonic()
        self.session.scheduler.metrics.observe("frame_interval", now - self.last_frame)
        self.last_frame = now
        for model in self.geometry_models():
            model.presented()

    @measured("publication", lambda owner: owner.session.profiler)
    def activate_geometry(self):
        from .image_scene import prepare_picking as prepare_images
        from .path_scene import prepare_picking

        scene_state.picking_inputs(self, self.render_model.active_rows())
        prepare_picking(self)
        prepare_images(self)
        from anthroforge.application.geometry_ownership import collect

        collect(self.session)
        self.notify()

    def refresh_if_needed(self):
        projection = self.scene_projection
        if (
            projection.session is not self.session
            or projection.cursor != self.session.changes.serial
            or self.last_workspace != self.session.active_workspace
            or getattr(self, "_conversion_key", None) != self.conversion_key()
        ):
            self.refresh()

    @measured("ui", lambda owner: owner.session.profiler)
    def refresh(self):
        scene_projection.refresh(self)
        self.creation_selection.synchronize()
        self.last_revision = self.session.document.revision
        self.last_workspace = self.session.active_workspace
        self._conversion_key = self.conversion_key()
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

    @Slot(str, "QVariantMap", result="QVariant")
    def createConstruction(self, operation, arguments):
        return self.creation_selection.create(operation, arguments)

    @Slot(str)
    @Slot(str, bool)
    def select(self, entity, extend=False):
        self.object_selection.choose(entity, extend)
        if (
            self.session.tissue_preview.target
            and self.session.tissue_preview.target != self.selection
        ):
            from anthroforge.application.tissue_preview import cancel

            cancel(self.session)
        self.scene_projection.synchronize_selection()
        self.scene_projection.publish_records()
        self.authoring.refresh()
        self.notify()

    @Slot(str, result="QVariantMap")
    def objectRecord(self, target):
        return self.scene_projection.records.get(target) or self.construction.records.get(
            target, {}
        )

    @Slot(str, float, str, bool)
    def importMesh(self, path, units, parent, y_up):
        result = self.run(
            "import",
            {"path": actions.local_path(path), "units": units, "parent": parent, "y_up": y_up},
        )
        if result:
            self.message = "Import queued. You can keep navigating and editing."

    @Slot("QVariantList", "QVariantList", int, bool, float, result="QVariantMap")
    @Slot("QVariantList", "QVariantList", int, bool, float, bool, result="QVariantMap")
    def pick(self, origin, direction, depth, select, radius=0.03, extend=False):
        self.last_hit = scene_state.picked(self, origin, direction, depth, radius)
        previous = self.hovered
        self.hovered = self.last_hit.get("id", "")
        if select:
            self.select(self.hovered, extend)
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
        self.numeric_edits.cancel()
        if hasattr(self, "feedback"):
            self.feedback.close()
            self.report_browser.close()
        self.drawing_tools.cancel()
        self.tissue_inspection.clear()
        self.session.close()
        self.profiler.close()
        for lock in self.temporary_locks:
            lock.close()
