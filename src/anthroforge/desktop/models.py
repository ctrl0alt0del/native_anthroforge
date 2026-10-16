"""Stable render delegates with bounded creation of geometry chunks."""

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class RenderModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = []
        self.pending = []

    def roleNames(self):
        return {Qt.ItemDataRole.UserRole + 1: b"item"}

    def rowCount(self, parent=None):
        return 0 if parent is not None and parent.isValid() else len(self.rows)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and role == Qt.ItemDataRole.UserRole + 1:
            return self.rows[index.row()]
        return None

    def publish(self, rows):
        wanted = {row["key"]: row for row in rows}
        self._remove_missing(wanted)
        self._update_existing(wanted)
        present = {row["key"] for row in self.rows}
        self.pending = [row for row in rows if row["key"] not in present]

    def _remove_missing(self, wanted):
        for index in range(len(self.rows) - 1, -1, -1):
            if self.rows[index]["key"] not in wanted:
                self.beginRemoveRows(QModelIndex(), index, index)
                self.rows.pop(index)
                self.endRemoveRows()

    def _update_existing(self, wanted):
        for index, row in enumerate(self.rows):
            changed = wanted[row["key"]]
            if changed != row:
                self.rows[index] = changed
                self.dataChanged.emit(self.index(index), self.index(index))

    def drain(self):
        for _ in range(min(2, len(self.pending))):
            row = self.pending.pop(0)
            index = len(self.rows)
            self.beginInsertRows(QModelIndex(), index, index)
            self.rows.append(row)
            self.endInsertRows()
