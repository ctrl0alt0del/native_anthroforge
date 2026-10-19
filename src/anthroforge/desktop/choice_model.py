"""Incremental choice membership and filtered bulk operations shared by bounded editors."""

from PySide6.QtCore import Property, QSortFilterProxyModel, Signal, Slot

from .record_model import RecordModel

FIELDS = ("key", "label", "detail", "chosen", "locked", "reason")


class ChoiceModel(QSortFilterProxyModel):
    changed = Signal()
    edited = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.records = RecordModel(self, FIELDS, "key")
        self.query, self.filter_mode = "", 0
        self.setSourceModel(self.records)

    @Property("QVariantMap", notify=changed)
    def counts(self):
        rows = self.records.rows
        return dict(total=len(rows), chosen=sum(r["chosen"] for r in rows), shown=self.rowCount())

    @Property("QVariantList", notify=changed)
    def selected(self):
        return [row["key"] for row in self.records.rows if row["chosen"]]

    @Slot("QVariantList")
    def synchronize(self, rows):
        if rows != self.records.rows:
            self.beginFilterChange()
            self.records.synchronize_records(rows)
            self.endFilterChange(self.Direction.Rows)
            self.changed.emit()

    @Slot(str, int)
    def filter(self, text, mode):
        self.beginFilterChange()
        self.query, self.filter_mode = text.casefold().strip(), mode
        self.endFilterChange(self.Direction.Rows)
        self.changed.emit()

    def filterAcceptsRow(self, index, parent):
        row = self.records.rows[index]
        matches = (
            self.query in (row["label"] + " " + row["detail"] + " " + row["reason"]).casefold()
        )
        return matches and (not self.filter_mode or row["chosen"] == (self.filter_mode == 1))

    @Slot(str, bool)
    def choose(self, key, value):
        self.update_choices({key}, value)

    @Slot(bool)
    def chooseShown(self, value):
        keys = {
            self.records.rows[self.mapToSource(self.index(i, 0)).row()]["key"]
            for i in range(self.rowCount())
        }
        self.update_choices(keys, value)

    def update_choices(self, keys, value):
        rows = [
            dict(row, chosen=value) if row["key"] in keys and not row["locked"] else row
            for row in self.records.rows
        ]
        if rows != self.records.rows:
            self.synchronize(rows)
            self.edited.emit(self.selected)
