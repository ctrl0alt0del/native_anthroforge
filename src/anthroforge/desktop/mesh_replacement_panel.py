"""Native mesh source selection uses the shared replacement-review lifecycle."""

from PySide6.QtCore import QUrl, Slot

from .replacement_panel import ReplacementPanel


class MeshReplacementPanel(ReplacementPanel):
    def __init__(self, controller):
        super().__init__(controller, "mesh_replacement", "scp.mesh.replace", "Replace source mesh")

    @Slot(str)
    def assess(self, url):
        path = QUrl(url).toLocalFile() if QUrl(url).isLocalFile() else url
        self.begin(dict(target=self.target, path=path))
