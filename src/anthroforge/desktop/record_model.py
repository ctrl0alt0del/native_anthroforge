"""Stable keyed records shared by diagnostic and Activity list adapters."""

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class RecordModel(QAbstractListModel):
    def __init__(self, parent, fields, key):
        super().__init__(parent)
        self.rows, self.key = [], key
        self.roles = {Qt.ItemDataRole.UserRole + i + 1: name for i, name in enumerate(fields)}

    def roleNames(self):
        return {role: name.encode() for role, name in self.roles.items()}

    def rowCount(self, parent=None):
        return 0 if parent is not None and parent.isValid() else len(self.rows)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and 0 <= index.row() < len(self.rows) and role in self.roles:
            return self.rows[index.row()][self.roles[role]]
        return None

    def synchronize_records(self, desired):
        self.remove_missing({row[self.key] for row in desired})
        for index, row in enumerate(desired):
            self.place(index, row)
            self.update_row(index, row)

    def remove_missing(self, wanted):
        for index in range(len(self.rows) - 1, -1, -1):
            if self.rows[index][self.key] not in wanted:
                self.beginRemoveRows(QModelIndex(), index, index)
                self.rows.pop(index)
                self.endRemoveRows()

    def place(self, index, row):
        ids = [item[self.key] for item in self.rows]
        if row[self.key] not in ids:
            self.beginInsertRows(QModelIndex(), index, index)
            self.rows.insert(index, row)
            self.endInsertRows()
        elif ids.index(row[self.key]) != index:
            source = ids.index(row[self.key])
            self.beginMoveRows(QModelIndex(), source, source, QModelIndex(), index)
            self.rows.insert(index, self.rows.pop(source))
            self.endMoveRows()

    def update_row(self, index, row):
        changed = [role for role, name in self.roles.items() if self.rows[index][name] != row[name]]
        if changed:
            self.rows[index] = row
            self.dataChanged.emit(self.index(index), self.index(index), changed)
