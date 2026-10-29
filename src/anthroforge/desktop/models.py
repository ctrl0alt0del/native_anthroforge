"""Stable render delegates with bounded creation of geometry chunks."""

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Signal

from anthroforge.profiling.spans import measured


def model_profiler(model):
    session = getattr(model.parent(), "session", None)
    return session.profiler if session else None


class RenderModel(QAbstractListModel):
    activated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = []
        self.pending = []
        self.wanted = {}
        self.leases = {}
        self.frame = 0
        self.staged_frame = 0
        self.displayed = []
        self.publication_group = None

    def roleNames(self):
        return {Qt.ItemDataRole.UserRole + 1: b"item"}

    def rowCount(self, parent=None):
        return 0 if parent is not None and parent.isValid() else len(self.rows)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and role == Qt.ItemDataRole.UserRole + 1:
            return self.rows[index.row()]
        return None

    @measured("publication", model_profiler)
    def publish(self, rows, resources=()):
        self.wanted = {row["key"]: row for row in rows}
        self.leases.update({resource.handle: resource for resource in resources})
        owners = {row["id"] for row in rows}
        keep = {row["key"] for row in self.rows if row["active"] and row["id"] in owners}
        self._remove_missing(keep | self.wanted.keys())
        self._update_existing(self.wanted)
        present = {row["key"] for row in self.rows}
        self.pending = [dict(row, active=False) for row in rows if row["key"] not in present]
        self._collect_leases()

    def _remove_missing(self, wanted):
        for index in range(len(self.rows) - 1, -1, -1):
            if self.rows[index]["key"] not in wanted:
                self.beginRemoveRows(QModelIndex(), index, index)
                self.rows.pop(index)
                self.endRemoveRows()

    def _update_existing(self, wanted):
        owners = {row["id"]: row for row in wanted.values()}
        for index, row in enumerate(self.rows):
            changed = presentation(row, wanted.get(row["key"], owners.get(row["id"], row)))
            if changed != row:
                self.rows[index] = changed
                self.dataChanged.emit(self.index(index), self.index(index))

    @measured("publication", model_profiler)
    def drain(self):
        for _ in range(min(2, len(self.pending))):
            row = self.pending.pop(0)
            index = len(self.rows)
            self.beginInsertRows(QModelIndex(), index, index)
            self.rows.append(row)
            self.endInsertRows()
            self.staged_frame = self.frame

    @measured("publication", model_profiler)
    def presented(self):
        self.frame += 1
        self._record_displayed()
        if self.pending or self.staged_frame >= self.frame:
            return
        if self.publication_group and not self.publication_group.ready():
            return
        self._remove_missing(self.wanted)
        for index, row in enumerate(self.rows):
            if not row["active"]:
                self.rows[index] = dict(row, active=True)
                self.dataChanged.emit(self.index(index), self.index(index))
        self._collect_leases()

    def _record_displayed(self):
        rows = [row for row in self.rows if row["active"]]
        if rows != self.displayed:
            self.displayed = rows
            self.activated.emit()

    def active_rows(self):
        return list({row["id"]: row for row in self.displayed}.values())

    def _collect_leases(self):
        used = {row["handle"] for row in (*self.rows, *self.pending, *self.displayed)}
        self.leases = {key: value for key, value in self.leases.items() if key in used}

    def memory_owners(self, owners):
        staged = [row for row in self.rows if not row["active"]] + self.pending
        for name, rows in (("viewport_displayed", self.displayed), ("viewport_staging", staged)):
            handles = {row["handle"] for row in rows}
            for key, value in self.leases.items():
                if key in handles:
                    owners[name].add(value)
                    owners[name].update(getattr(value, "resources", ()))


class PublicationGroup:
    """A frame barrier for related views, independent of their feature/controller."""

    def __init__(self, models):
        self.models = tuple(models)
        for model in self.models:
            model.publication_group = self

    def ready(self):
        return not any(model.pending for model in self.models)


def presentation(previous, current):
    return dict(
        current,
        active=previous["active"],
        key=previous["key"],
        handle=previous["handle"],
        chunk=previous["chunk"],
        geometry_asset=previous.get("geometry_asset", ""),
        geometry_revision=previous.get("geometry_revision", 0),
        content=previous.get("content", {})
        if previous["key"] != current["key"]
        else current.get("content", {}),
    )
