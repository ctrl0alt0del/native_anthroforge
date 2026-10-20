import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: panel
    required property var curve
    Layout.fillWidth: true
    Label { text: "Path engine"; color: Theme.muted }
    UiCombo {
        id: engine
        objectName: panel.objectName + "Choice"
        Layout.fillWidth: true
        model: ["BEZIER", "POLYLINE", "ROUTED"]
        currentIndex: Math.max(0, model.indexOf(panel.curve.engine || "BEZIER"))
        hint: "Change the path using the existing control points. Undo restores the previous engine."
        onActivated: index => {
            workspace.run("curve.engine", {curve: panel.curve.id, engine: model[index]});
            currentIndex = Qt.binding(() => Math.max(0, model.indexOf(panel.curve.engine || "BEZIER")));
        }
    }
}
