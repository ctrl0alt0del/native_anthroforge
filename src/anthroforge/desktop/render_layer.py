"""Presentation layers filter staged rows without moving live nodes between Qt scenes."""

from PySide6.QtCore import Property, QSortFilterProxyModel, Qt, Signal


class RenderLayer(QSortFilterProxyModel):
    countChanged = Signal()

    def __init__(self, source, layer):
        super().__init__(source)
        self.layer = layer
        self.setSourceModel(source)
        self.rowsInserted.connect(self.countChanged)
        self.rowsRemoved.connect(self.countChanged)
        self.modelReset.connect(self.countChanged)

    @Property(int, notify=countChanged)
    def count(self):
        return self.rowCount()

    def filterAcceptsRow(self, row, parent):
        source = self.sourceModel()
        record = source.data(source.index(row, 0, parent), Qt.ItemDataRole.UserRole + 1)
        return record.get("content", {}).get("layer") == self.layer
