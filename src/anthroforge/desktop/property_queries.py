"""Property metadata subscriptions, independent of evaluated geometry revisions."""

from collections import OrderedDict

from PySide6.QtCore import Property, QObject, Signal
from PySide6.QtQml import QQmlPropertyMap

from anthroforge.core.numeric_properties import decode_reference
from anthroforge.core.snapshot_definitions import same


class PropertyQueries(QObject):
    epochsChanged = Signal()

    def __init__(self, panel):
        super().__init__(panel)
        self.panel, self.session, self.context = panel, None, None
        self.epochs = QQmlPropertyMap(self)
        self.records, self.cache, self.exposed = {}, OrderedDict(), set()
        self.shortcuts = None
        self.serial = 0
        self.document = None

    @Property(QObject, notify=epochsChanged)
    def versions(self):
        return self.epochs

    def reset(self, session):
        previous = self.epochs
        self.epochs = QQmlPropertyMap(self)
        self.session, self.context, self.shortcuts = session, None, None
        self.document = None
        self.records.clear()
        self.cache.clear()
        self.epochsChanged.emit()
        previous.deleteLater()

    def synchronize(self):
        session = self.panel.controller.session
        if session is not self.session:
            self.reset(session)
        document = session.document
        if document is self.document:
            return
        self.document = document
        changed = self.update_context(document)
        for key, previous in tuple(self.records.items()):
            current = document.registry.records.get(key)
            self.records[key] = current
            if changed or not equivalent(previous, current):
                self.invalidate(key)

    def update_context(self, document):
        context = (document.index.structure, document.driving_shortcuts, document.shortcuts)
        changed = self.context is None or any(
            a is not b for a, b in zip(context, self.context, strict=True)
        )
        self.context = context
        if self.shortcuts is not document.shortcuts:
            self.shortcuts = document.shortcuts
            self.exposed = {s.id for s in self.shortcuts if s.exposed}
        return changed

    def invalidate(self, key):
        self.serial += 1
        self.epochs.insert(key, self.serial)

    def state(self, reference):
        from .shortcut_panel import property_state

        self.synchronize()
        ref = decode_reference(reference)
        self.records[ref.target] = self.session.document.registry.records.get(ref.target)
        key = (ref, self.epochs.value(ref.target))
        if key not in self.cache:
            self.cache[key] = property_state(self.session, reference, self.exposed)
        self.cache.move_to_end(key)
        while len(self.cache) > 4096:
            self.cache.popitem(last=False)
        return self.cache[key]


def equivalent(before, after):
    return before is after or before is not None and after is not None and same(before, after)
