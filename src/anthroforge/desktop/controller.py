from time import perf_counter as monotonic
from weakref import WeakMethod

from PySide6.QtCore import QObject, QTimer, Signal, Slot

from anthroforge.application.session import Session
from anthroforge.native import scene
from anthroforge.profiling import RuntimeProfiler
from anthroforge.profiling.spans import measured

from . import controller_actions as actions
from . import project_actions, scene_projection, scene_state
from .activity_model import ActivityModel
from .assembly_panel import AssemblyPanel
from .creation_selection import CreationSelection
from .display_transforms import DisplayTransforms
from .drawing_tools import DrawingTools
from .fiber_display import FiberDisplay
from .image_tools import ImageTools
from .inspection_export import InspectionExport
from .inspection_panel import InspectionPanel
from .inspection_tools import InspectionTools
from .issue_panel import IssuePanel
from .mesh_replacement_panel import MeshReplacementPanel
from .models import RenderModel
from .neighborhood_tools import NeighborhoodTools
from .numeric_edits import NumericEdits
from .placement_inspection_tools import PlacementInspectionTools
from .reconstruction_compare_panel import ReconstructionComparePanel
from .reconstruction_panel import ReconstructionPanel
from .route_inspection_tools import RouteInspectionTools
from .routing_choices import RoutingChoices
from .section_tools import SectionTools
from .shortcut_comparison_view import ShortcutComparisonView
from .shortcut_panel import ShortcutPanel
from .skeleton_panel import SkeletonPanel
from .skin_panel import SkinPanel
from .spatial_evidence_tools import SpatialEvidenceTools
from .surface_creation import SurfaceCreation
from .surface_measurement_tools import SurfaceMeasurementTools
from .tissue_inspection_tools import TissueInspectionTools
from .tissue_region_tools import TissueRegionTools
from .tissue_retarget_panel import TissueRetargetPanel
from .variant_panel import VariantPanel
from .weight_painting_tools import WeightPaintingTools


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
        self.initialize_views()
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

    def initialize_views(self):
        from .view_models.composition import attach

        attach(self)

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
        self.initialize_project_tools()

    def initialize_project_tools(self):
        self.mesh_replacement = MeshReplacementPanel(self)
        self.assembly_panel = AssemblyPanel(self)
        self.skeleton_panel = SkeletonPanel(self)
        self.variant_panel = VariantPanel(self)
        self.reconstruction_panel = ReconstructionPanel(self)
        self.reconstruction_compare = ReconstructionComparePanel(self)

    def initialize_tissue_tools(self):
        self.spatial_evidence = SpatialEvidenceTools(self)
        self.surface_measurements = SurfaceMeasurementTools(self)
        self.neighborhood = NeighborhoodTools(self)
        self.placement_inspection = PlacementInspectionTools(self)
        self.skin_panel = SkinPanel(self)
        self.shortcut_comparison = ShortcutComparisonView(self)
        self.shortcut_panel = ShortcutPanel(self)
        self.tissue_region_tools = TissueRegionTools(self)
        self.tissue_inspection = TissueInspectionTools(self)
        self.tissue_painting = WeightPaintingTools(self)
        self.section_tools = SectionTools(self)
        self.route_inspection = RouteInspectionTools(self)
        self.tissue_retarget = TissueRetargetPanel(self)

    def memory_owners(self, owners):
        from .feedback_comparison import memory_owners

        if hasattr(self, "feedback"):
            memory_owners(self.feedback, owners)
        for model in self.geometry_models():
            model.memory_owners(owners)
        self.fiber_display.memory_owners(owners)
        owners["drawing_preview"].update(self.drawing_tools.leases)
        if self.drawing_tools.stroke is not None:
            owners["drawing_preview"].add(self.drawing_tools.stroke)
        if self.tissue_painting.preview:
            owners["drawing_preview"].add(self.tissue_painting.preview["resource"])

    def geometry_models(self):
        return (
            self.render_model,
            self.path_model,
            self.fiber_display.model,
            self.image_model,
            self.tissue_inspection.model,
            self.tissue_painting.model,
            self.shortcut_comparison.model,
            self.shortcut_comparison.images,
            self.spatial_evidence.model,
        ) + self.comparison_models()

    def comparison_models(self):
        return (
            self.skeleton_panel.scene.models
            + self.variant_panel.scene.models
            + self.reconstruction_compare.scene.models
        )

    def initialize_renderers(self):
        from .image_scene import prepare_picking as prepare_images
        from .path_scene import prepare_picking

        self.render_model, self.path_model = RenderModel(self), RenderModel(self)
        self.image_model = RenderModel(self)
        self.fiber_display = FiberDisplay(self)
        self.initialize_image_layers()
        self.render_model.activated.connect(self.activate_geometry)
        self.path_model.activated.connect(self.activate_geometry)
        self.path_model.activated.connect(self.drawing_tools.branch.invalidate)
        self.image_model.activated.connect(self.activate_geometry)
        prepare_picking(self)
        prepare_images(self)
        self.surface_measurements.watch_display()

    def initialize_image_layers(self):
        from .render_layer import RenderLayer

        self._presenting = self._geometry_dirty = False
        self.display_transforms = DisplayTransforms()
        self.image_layers = {
            key: RenderLayer(self.image_model, key) for key in ("NORMAL", "FRONT", "BACK")
        }
        self.viewport_view.orthographic = False
        self.viewport_view.direction = (0, 0, 1)

    def _initialize_state(self):
        self.selection, self.selection_view.hovered, self.message = "", "", ""
        self.last_revision, self.last_workspace = -1, -1
        self.rows, self.viewport_view.drag_values, self.pick_ids = [], [], []
        self.project_view.initialize()
        self.viewport_view.drag_mode = "Move"
        self.selection_view.last_hit = {}
        self.tick_count = 0
        self.viewport_view.camera_workspace = None
        self.capture_mode = False
        self.last_frame = monotonic()

    @property
    def selection(self):
        return self.selection_view.objects.primary

    @selection.setter
    def selection(self, value):
        self.selection_view.objects.choose(value)

    def conversion_key(self):
        return tuple(
            (v.token, v.state, id(v.asset))
            for v in (
                self.session.conversion,
                self.session.surface_preview,
                self.session.tissue_preview,
                self.session.skin_fit_preview,
            )
        )

    @measured("ui", lambda owner: owner.session.profiler)
    def notify(self):
        self.shortcut_panel.property_queries.synchronize()
        self.runtime_view.synchronize()
        self.changed.emit()
        names = {row["id"]: row["name"] for row in self.rows}
        self.activity_model.synchronize(self.session.scheduler.jobs, names)
        self.runtime_view.refresh_metrics()
        self.issue_panel.synchronize()
        self.mesh_replacement.synchronize()
        self.tissue_retarget.synchronize()
        self.inspection_panel.synchronize()
        self.inspection_export.synchronize()
        self.refresh_viewport_tools()

    def refresh_viewport_tools(self):
        self.shortcut_panel.synchronize()
        self.inspection_tools.synchronize()
        self.image_tools.synchronize()
        self.drawing_tools.synchronize()
        self.tissue_region_tools.synchronize()
        self.tissue_painting.synchronize()
        self.tissue_inspection.synchronize()
        self.section_tools.synchronize()
        self.route_inspection.synchronize()

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
        self.refresh_runtime_panels()
        self.tick_count += 1
        if self.tick_count % 15 == 0:
            self.notify()

    def refresh_runtime_panels(self):
        self.refresh_reconstruction_panels()
        self.assembly_panel.synchronize()
        self.skeleton_panel.synchronize()
        self.spatial_evidence.synchronize()
        self.surface_measurements.synchronize()
        self.neighborhood.synchronize()
        self.placement_inspection.synchronize()
        self.shortcut_comparison.synchronize()
        self.creation_selection.synchronize()
        self.issue_panel.synchronize()
        self.mesh_replacement.synchronize()
        self.tissue_retarget.synchronize()
        self.shortcut_panel.synchronize()

    def refresh_reconstruction_panels(self):
        self.reconstruction_panel.synchronize()
        self.variant_panel.synchronize()
        self.reconstruction_compare.synchronize()

    @Slot()
    def frame_presented(self):
        now = monotonic()
        self.session.scheduler.metrics.observe("frame_interval", now - self.last_frame)
        self.last_frame = now
        self._presenting = True
        try:
            for model in self.geometry_models():
                model.presented()
        finally:
            self._presenting = False
        if self._geometry_dirty:
            self._geometry_dirty = False
            self.activate_geometry()

    @measured("publication", lambda owner: owner.session.profiler)
    def activate_geometry(self):
        if self._presenting:
            self._geometry_dirty = True
            return
        self.publish_displayed()

    def publish_displayed(self):
        from .image_scene import prepare_picking as prepare_images
        from .path_scene import prepare_picking

        scene_state.picking_inputs(self, self.render_model.active_rows())
        prepare_picking(self)
        prepare_images(self)
        from anthroforge.application.geometry_ownership import collect

        collect(self.session)
        self.shortcut_panel.display_changed()
        self.notify()

    def refresh_if_needed(self):
        projection = self.scene_projection
        if (
            projection.session is not self.session
            or projection.journal is not self.session.changes
            or projection.context != self.session._editing.key
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
        self.viewport_view.restore_camera()

    def run(self, operation, arguments):
        self.shortcut_comparison.editing(operation)
        return actions.run(self, operation, arguments)

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
        for lock in self.project_view.temporary_locks:
            lock.close()
