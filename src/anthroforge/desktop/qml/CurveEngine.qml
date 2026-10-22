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
        model: panel.curve.bindings !== undefined ? ["BEZIER", "POLYLINE", "ROUTED"] : ["BEZIER", "POLYLINE", "ROUTED", "PARAMETRIC"]
        currentIndex: Math.max(0, model.indexOf(panel.curve.engine || "BEZIER"))
        hint: "Change the path engine directly. Parametric restores its equations; switching away keeps generated points. Undo restores the previous engine."
        onActivated: index => {
            workspace.run("curve.engine", {curve: panel.curve.id, engine: model[index]});
            currentIndex = Qt.binding(() => Math.max(0, model.indexOf(panel.curve.engine || "BEZIER")));
        }
    }
}
