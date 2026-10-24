import QtQuick
import QtQuick.Layouts

ColumnLayout {
    required property var adapter
    required property var details
    readonly property var descriptor: adapter.propertyValue
    ShortcutValues { Layout.fillWidth: true; shortcutKey: details.id || ""; reference: details.reference || ({}); values: descriptor.values || []; numericType: descriptor.numericType || "REAL"; dimension: descriptor.dimension || "SCALAR"; writable: !!descriptor.writable; onEdited: (component,value) => adapter.editProperty(component,value) }
}
