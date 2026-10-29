"""Reconstruction navigation invokes the same scoped operations as headless clients."""

import json

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot


class ReconstructionPanel(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self._open, self._floating = False, False
        self._signature, self._data = None, "{}"
        self._page = "Variants"
        self.stage_path = ""

    @Property(str, notify=changed)
    def page(self):
        return self._page

    @Slot(str)
    def setPage(self, page):
        self._page, self._signature = page, None
        self.synchronize()

    @Property(str, notify=changed)
    def dataJson(self):
        return self._data

    @Property(bool, notify=changed)
    def opened(self):
        return self._open

    @Property(bool, notify=changed)
    def floating(self):
        return self._floating

    @Slot(bool)
    def setOpen(self, value):
        self._open = value
        self.synchronize()
        self.changed.emit()

    @Slot(bool)
    def setFloating(self, value):
        self._floating = value
        self.changed.emit()

    def synchronize(self):
        session = self.controller.session
        root = session.contexts.scene("")
        signature = (id(root.reconstruction), session.contexts.visible, self._page)
        if self._page in ("Reviews", "Variants", "Regions"):
            signature += (id(session.document), id(root), self.controller.selection)
        if self._page == "Stages":
            signature += (self.stage_path, session.assembly.source.state)
        if signature == self._signature:
            return
        self._signature = signature
        self._data = json.dumps(self.projection())
        self.changed.emit()

    def projection(self):
        session = self.controller.session
        result = session.command("variant.inspect")
        commands = {
            "Catalogue": "catalogue.inspect",
            "Regions": "catalogue.inspect",
            "Reviews": "review.inspect",
            "Queue": "reconstruction.queue.inspect",
            "Stages": "reconstruction.stage.inspect",
        }
        if self._page in commands:
            result["detail"] = session.command(commands[self._page])
        return dict(result, **self.related_records())

    def related_records(self):
        session = self.controller.session
        result = {}
        result["evidence"] = session.command("reconstruction.evidence.inspect")["evidence"]
        result["source"] = self.source_state()
        result["reviewStages"] = self.review_stages() if self._page == "Reviews" else []
        result["regions"] = [
            vars_region(r) for r in session.contexts.project().reconstruction.regions
        ]
        return result

    def review_stages(self):
        from anthroforge.application.reconstruction_views import options

        try:
            return options(self.controller.session, self.controller.selection)["views"]
        except ValueError:
            return []

    def source_state(self):
        source = self.controller.session.assembly.source
        return dict(
            path=self.stage_path,
            state=source.state,
            error=source.error,
            inventory=source.inventory if self.stage_path.endswith(".anthroforge") else [],
        )

    @Slot(str)
    def chooseStageFile(self, url):
        self.stage_path = QUrl(url).toLocalFile()
        if self.stage_path.endswith(".anthroforge"):
            self.controller.run("assembly.inspect", dict(path=self.stage_path))
        self._signature = None
        self.synchronize()

    @Slot(str, float, bool, "QVariantList", str, str)
    def importStage(self, stage, units, y_up, transform, source_entity, role):
        session = self.controller.session
        arguments = dict(
            subject=self.controller.selection,
            stage=stage,
            path=self.stage_path,
            variant=session.contexts.visible,
            frame=session.engine.transform(transform),
        )
        if self.stage_path.endswith(".anthroforge"):
            arguments.update(source_entity=source_entity, role=role)
            self.run("reconstruction.stage.import_project", arguments)
        else:
            arguments.update(units=units, y_up=y_up)
            self.run("reconstruction.stage.import_mesh", arguments)

    @Slot(str)
    def importEvidence(self, url):
        self.run("reconstruction.evidence.import_file", dict(path=QUrl(url).toLocalFile()))

    @Slot(str, str)
    def exportEvidence(self, evidence, url):
        self.run(
            "reconstruction.evidence.export", dict(evidence=evidence, path=QUrl(url).toLocalFile())
        )

    @Slot("QVariantMap")
    def resumeWork(self, row):
        variant = row.get("variant", "")
        self.run("variant.enter" if variant else "variant.leave", dict(variant=variant))
        self.selectMembers([row["subject"]])

    @Slot(str, str)
    def assignSelection(self, type_id, side):
        self.run(
            "catalogue.assign_many",
            dict(
                targets=self.controller.selectedObjects,
                type_id=type_id,
                side=side,
                variant=self.controller.session.contexts.visible,
            ),
        )

    @Slot("QVariantList")
    def selectMembers(self, identities):
        session = self.controller.session
        selected = [key for key in identities if key in session.document.registry.records]
        self.controller.selectObjects(selected)

    @Slot()
    def create(self):
        session = self.controller.session
        subjects = [
            key
            for key in self.controller.selectedObjects
            if key in session.document.registry.anatomy
        ]
        self.run("variant.create", dict(subjects=subjects))

    @Slot(str, "QVariantMap", result="QVariant")
    def run(self, operation, arguments):
        controller = self.controller
        before = controller.session.contexts.visible
        result = controller.run(operation, arguments)
        if before != controller.session.contexts.visible:
            controller.authoring.setEditing(False)
            controller.drawing_tools.cancel()
            controller.refresh()
        self._signature = None
        self.synchronize()
        return result


def vars_region(row):
    from dataclasses import asdict

    return asdict(row)
