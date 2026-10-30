"""Typed QML composition, scoped to its engine; panel models own all behavior."""

from PySide6.QtCore import Property, QObject
from PySide6.QtQml import QmlElement, QmlSingleton

from .activity_model import ActivityModel
from .assembly_panel import AssemblyPanel
from .authoring import Authoring
from .drawing_tools import DrawingTools
from .feedback_editor import FeedbackEditor
from .image_tools import ImageTools
from .input_state import InputState
from .inspection_export import InspectionExport
from .inspection_panel import InspectionPanel
from .inspection_tools import InspectionTools
from .issue_panel import IssuePanel
from .mesh_replacement_panel import MeshReplacementPanel
from .neighborhood_tools import NeighborhoodTools
from .numeric_edits import NumericEdits
from .placement_inspection_tools import PlacementInspectionTools
from .preference_controls import PreferenceControls
from .profile_controls import ProfileControls
from .project_library import ProjectLibrary
from .qml_model_types import register
from .reconstruction_compare_panel import ReconstructionComparePanel
from .reconstruction_panel import ReconstructionPanel
from .report_browser import ReportBrowser
from .route_inspection_tools import RouteInspectionTools
from .section_tools import SectionTools
from .shortcut_comparison_view import ShortcutComparisonView
from .shortcut_panel import ShortcutPanel
from .skeleton_panel import SkeletonPanel
from .skin_panel import SkinPanel
from .spatial_evidence_tools import SpatialEvidenceTools
from .surface_creation import SurfaceCreation
from .surface_measurement_tools import SurfaceMeasurementTools
from .system_integration import SystemIntegration
from .tissue_inspection_tools import TissueInspectionTools
from .tissue_region_tools import TissueRegionTools
from .tissue_retarget_panel import TissueRetargetPanel
from .variant_panel import VariantPanel
from .view_models.construction_view import ConstructionView
from .view_models.mirror_view import MirrorView
from .view_models.project_view import ProjectView
from .view_models.runtime_view import RuntimeView
from .view_models.selection_view import SelectionView
from .view_models.viewport_view import ViewportView
from .weight_painting_tools import WeightPaintingTools
from .workbench_state import WorkbenchState

TYPES = (
    InputState,
    ProjectLibrary,
    ShortcutPanel,
    SkinPanel,
    ShortcutComparisonView,
    TissueRetargetPanel,
    MeshReplacementPanel,
    AssemblyPanel,
    SkeletonPanel,
    ReconstructionPanel,
    ReconstructionComparePanel,
    VariantPanel,
    SpatialEvidenceTools,
    SurfaceMeasurementTools,
    NeighborhoodTools,
    PlacementInspectionTools,
    ActivityModel,
    IssuePanel,
    InspectionPanel,
    InspectionExport,
    InspectionTools,
    ImageTools,
    DrawingTools,
    TissueRegionTools,
    TissueInspectionTools,
    WeightPaintingTools,
    SectionTools,
    RouteInspectionTools,
    SurfaceCreation,
    Authoring,
    NumericEdits,
    PreferenceControls,
    SystemIntegration,
    WorkbenchState,
    ProfileControls,
    FeedbackEditor,
    ReportBrowser,
    ProjectView,
    SelectionView,
    ViewportView,
    ConstructionView,
    MirrorView,
    RuntimeView,
)

register(TYPES)

QML_IMPORT_NAME = "AnthroForge.Desktop"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@QmlSingleton
class App(QObject):
    def __init__(self, controller, inputs, engine):
        super().__init__(engine)
        self.controller = controller
        self.inputs = inputs

    @staticmethod
    def create(engine):
        if not hasattr(engine, "anthroforge_models"):
            raise RuntimeError("Bind the AnthroForge models before loading QML.")
        return engine.anthroforge_models

    @Property(InputState, constant=True)
    def heldInput(self):
        return self.inputs

    @Property(ProjectLibrary, constant=True)
    def projectLibrary(self):
        return self.controller.project_view.library

    @Property(ShortcutPanel, constant=True)
    def shortcutPanel(self):
        return self.controller.shortcut_panel

    @Property(SkinPanel, constant=True)
    def skinPanel(self):
        return self.controller.skin_panel

    @Property(ShortcutComparisonView, constant=True)
    def shortcutComparison(self):
        return self.controller.shortcut_comparison

    @Property(TissueRetargetPanel, constant=True)
    def tissueRetarget(self):
        return self.controller.tissue_retarget

    @Property(MeshReplacementPanel, constant=True)
    def meshReplacement(self):
        return self.controller.mesh_replacement

    @Property(AssemblyPanel, constant=True)
    def assemblyPanel(self):
        return self.controller.assembly_panel

    @Property(SkeletonPanel, constant=True)
    def skeletonPanel(self):
        return self.controller.skeleton_panel

    @Property(ReconstructionPanel, constant=True)
    def reconstructionPanel(self):
        return self.controller.reconstruction_panel

    @Property(ReconstructionComparePanel, constant=True)
    def reconstructionCompare(self):
        return self.controller.reconstruction_compare

    @Property(VariantPanel, constant=True)
    def variantPanel(self):
        return self.controller.variant_panel

    @Property(SpatialEvidenceTools, constant=True)
    def spatialEvidence(self):
        return self.controller.spatial_evidence

    @Property(SurfaceMeasurementTools, constant=True)
    def surfaceMeasurements(self):
        return self.controller.surface_measurements

    @Property(NeighborhoodTools, constant=True)
    def neighborhoodView(self):
        return self.controller.neighborhood

    @Property(PlacementInspectionTools, constant=True)
    def placementInspection(self):
        return self.controller.placement_inspection

    @Property(ActivityModel, constant=True)
    def activityModel(self):
        return self.controller.activity_model

    @Property(IssuePanel, constant=True)
    def issuePanel(self):
        return self.controller.issue_panel

    @Property(InspectionPanel, constant=True)
    def inspectionPanel(self):
        return self.controller.inspection_panel

    @Property(InspectionExport, constant=True)
    def inspectionExport(self):
        return self.controller.inspection_export

    @Property(InspectionTools, constant=True)
    def inspectionTools(self):
        return self.controller.inspection_tools

    @Property(ImageTools, constant=True)
    def imageTools(self):
        return self.controller.image_tools

    @Property(DrawingTools, constant=True)
    def drawingTools(self):
        return self.controller.drawing_tools

    @Property(TissueRegionTools, constant=True)
    def tissueRegionTools(self):
        return self.controller.tissue_region_tools

    @Property(TissueInspectionTools, constant=True)
    def tissueInspection(self):
        return self.controller.tissue_inspection

    @Property(WeightPaintingTools, constant=True)
    def tissuePainting(self):
        return self.controller.tissue_painting

    @Property(SectionTools, constant=True)
    def sectionTools(self):
        return self.controller.section_tools

    @Property(RouteInspectionTools, constant=True)
    def routeInspection(self):
        return self.controller.route_inspection

    @Property(SurfaceCreation, constant=True)
    def surfaceCreation(self):
        return self.controller.surface_creation

    @Property(Authoring, constant=True)
    def authoring(self):
        return self.controller.authoring

    @Property(NumericEdits, constant=True)
    def numericEdits(self):
        return self.controller.numeric_edits

    @Property(PreferenceControls, constant=True)
    def preferences(self):
        return self.controller.preference_controls

    @Property(SystemIntegration, constant=True)
    def systemIntegration(self):
        return self.controller.system_integration

    @Property(WorkbenchState, constant=True)
    def workbench(self):
        return self.controller.workbench

    @Property(ProfileControls, constant=True)
    def performance(self):
        return self.controller.profile_controls

    @Property(FeedbackEditor, constant=True)
    def feedback(self):
        return self.controller.feedback

    @Property(ReportBrowser, constant=True)
    def reportBrowser(self):
        return self.controller.report_browser

    @Property(ProjectView, constant=True)
    def project(self):
        return self.controller.project_view

    @Property(SelectionView, constant=True)
    def selection(self):
        return self.controller.selection_view

    @Property(ViewportView, constant=True)
    def viewport(self):
        return self.controller.viewport_view

    @Property(ConstructionView, constant=True)
    def construction(self):
        return self.controller.construction_view

    @Property(MirrorView, constant=True)
    def mirrors(self):
        return self.controller.mirror_view

    @Property(RuntimeView, constant=True)
    def runtime(self):
        return self.controller.runtime_view
