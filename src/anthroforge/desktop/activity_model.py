"""Stable, bounded Activity rows with role-specific updates on the GUI thread."""

from time import perf_counter

from PySide6.QtCore import Property, QAbstractListModel, QModelIndex, Qt, Signal

from .activity_rows import job_row

FIELDS = (
    "jobId",
    "label",
    "jobState",
    "error",
    "progress",
    "elapsed",
    "targets",
    "retryable",
    "cancellable",
    "scheduling",
)
ROLES = {Qt.ItemDataRole.UserRole + index + 1: name for index, name in enumerate(FIELDS)}
HISTORY_LIMIT = 40


class ActivityModel(QAbstractListModel):
    summaryChanged = Signal()

    def __init__(self, parent=None, clock=perf_counter):
        super().__init__(parent)
        self.setObjectName("activityJobs")
        self.rows, self.clock = [], clock
        self._active, self._failed = 0, False

    def roleNames(self):
        return {role: name.encode() for role, name in ROLES.items()}

    def rowCount(self, parent=None):
        return 0 if parent is not None and parent.isValid() else len(self.rows)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and 0 <= index.row() < len(self.rows) and role in ROLES:
            return self.rows[index.row()][ROLES[role]]
        return None

    @Property(int, notify=summaryChanged)
    def activeCount(self):
        return self._active

    @Property(bool, notify=summaryChanged)
    def hasFailures(self):
        return self._failed

    def synchronize(self, jobs, names):
        now = self.clock()
        desired = [job_row(job, names, now) for job in reversed(jobs[-HISTORY_LIMIT:])]
        self.remove_missing({row["jobId"] for row in desired})
        for index, row in enumerate(desired):
            self.place(index, row)
            self.update_row(index, row)
        self.update_summary()

    def remove_missing(self, wanted):
        for index in range(len(self.rows) - 1, -1, -1):
            if self.rows[index]["jobId"] not in wanted:
                self.beginRemoveRows(QModelIndex(), index, index)
                self.rows.pop(index)
                self.endRemoveRows()

    def place(self, index, row):
        ids = [item["jobId"] for item in self.rows]
        if row["jobId"] not in ids:
            self.beginInsertRows(QModelIndex(), index, index)
            self.rows.insert(index, row)
            self.endInsertRows()
        elif ids.index(row["jobId"]) != index:
            source = ids.index(row["jobId"])
            self.beginMoveRows(QModelIndex(), source, source, QModelIndex(), index)
            self.rows.insert(index, self.rows.pop(source))
            self.endMoveRows()

    def update_row(self, index, row):
        changed = [role for role, name in ROLES.items() if self.rows[index][name] != row[name]]
        if changed:
            self.rows[index] = row
            self.dataChanged.emit(self.index(index), self.index(index), changed)

    def update_summary(self):
        active = sum(row["cancellable"] for row in self.rows)
        failed = any(row["jobState"] == "failed" for row in self.rows)
        if (active, failed) != (self._active, self._failed):
            self._active, self._failed = active, failed
            self.summaryChanged.emit()
