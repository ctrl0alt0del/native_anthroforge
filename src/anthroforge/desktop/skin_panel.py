"""Small skin settings projection, separate from anatomy selection and computed payloads."""

from dataclasses import asdict

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import skin_builder_configuration, skin_pipeline_status, skin_reports

from . import skin_contributor
from .controller_actions import local_path
from .skin_export import SkinExport
from .skin_fit_panel import SkinFitPanel
from .values import qml


class SkinPanel(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.current = None
        self.display = None
        self.values = {}
        self.fitting = SkinFitPanel(controller)
        self.exporting = SkinExport(controller)
        controller.changed.connect(self.refresh)
        controller.selectionChanged.connect(self.refresh)
        self.unsubscribe = controller.session.skin_status.subscribe(self.changed.emit)
        self.refresh()

    def refresh(self):
        skin = self.controller.session.document.skin
        session = self.controller.session
        display = context(self.controller, session)
        if skin is self.current and display == self.display:
            return
        self.current = skin
        self.display = display
        self.values = authored(skin) | dict(
            display=display[0],
            contributor=skin_contributor.describe(session, display[1]),
            reports=skin_reports.describe(session),
            pipeline=skin_pipeline_status.describe(session),
        )
        self.changed.emit()

    @Slot(str)
    def importDraftPlan(self, path):
        self.controller.run("skin.draft.plan.import", {"path": local_path(path)})

    @Property(dict, notify=changed)
    def state(self):
        return qml(self.values)

    @Property(dict, notify=changed)
    def readiness(self):
        return qml(self.controller.session.skin_status.describe()["operations"])

    @Property(QObject, constant=True)
    def fits(self):
        return self.fitting

    @Property(QObject, constant=True)
    def exporter(self):
        return self.exporting


def authored(skin):
    data = asdict(skin)
    data["configuration_state"] = configuration_state(skin)
    if skin.draft_settings.backend == "FIELD":
        data["envelope_settings"] = asdict(skin_builder_configuration.decode(skin).settings)
    return data


def configuration_state(skin):
    applied = skin.applied_draft
    if applied is None:
        return "Saved draft provenance unknown" if skin.envelope.asset else "No accepted draft yet"
    pending = skin.draft_settings.configuration() != applied.configuration
    return f"Applied: {applied.configuration.builder}" + (" · settings pending" if pending else "")


def context(controller, session):
    selected = controller.selection
    item = session.document.registry.records.get(selected)
    return (
        session.workspace.skin_display,
        selected,
        session.workspace,
        id(item),
        id(session.document.index.entities),
        tuple(skin_pipeline_status.describe(session).items()),
    )
