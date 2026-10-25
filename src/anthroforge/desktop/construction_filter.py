"""Search the existing Construction model without rebuilding or selecting records."""

from PySide6.QtCore import QSortFilterProxyModel, Slot


class ConstructionFilter(QSortFilterProxyModel):
    def __init__(self, source):
        super().__init__(source)
        self.query = ""
        self.setSourceModel(source)

    @Slot(str)
    def search(self, text):
        query = text.strip().casefold()
        if query != self.query:
            self.beginFilterChange()
            self.query = query
            self.endFilterChange(self.Direction.Rows)

    def filterAcceptsRow(self, index, parent):
        item = self.sourceModel().rows[index]["item"]
        return self.query in (item["name"] + " " + item["kind"]).casefold()
