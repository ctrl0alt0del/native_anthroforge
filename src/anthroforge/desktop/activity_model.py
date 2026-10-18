"""Stable, bounded Activity rows with role-specific updates on the GUI thread."""

from time import perf_counter

from PySide6.QtCore import Property, Qt, Signal

from .activity_rows import job_row
from .record_model import RecordModel

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


class ActivityModel(RecordModel):
    summaryChanged = Signal()

    def __init__(self, parent=None, clock=perf_counter):
        super().__init__(parent, FIELDS, "jobId")
        self.setObjectName("activityJobs")
        self.rows, self.clock = [], clock
        self._active, self._failed = 0, False

    @Property(int, notify=summaryChanged)
    def activeCount(self):
        return self._active

    @Property(bool, notify=summaryChanged)
    def hasFailures(self):
        return self._failed

    def synchronize(self, jobs, names):
        now = self.clock()
        desired = [job_row(job, names, now) for job in reversed(jobs[-HISTORY_LIMIT:])]
        self.synchronize_records(desired)
        self.update_summary()

    def update_summary(self):
        active = sum(row["cancellable"] for row in self.rows)
        failed = any(row["jobState"] == "failed" for row in self.rows)
        if (active, failed) != (self._active, self._failed):
            self._active, self._failed = active, failed
            self.summaryChanged.emit()
