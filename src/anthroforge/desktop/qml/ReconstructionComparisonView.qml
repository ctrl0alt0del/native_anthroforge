import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Layouts

RowLayout {
    property var service: App.reconstructionCompare.comparison
    SkeletonViewport { Layout.fillWidth: true; Layout.fillHeight: true; service: parent.service; side: 0; visible: ["Split","Before"].includes(service.state.mode) }
    SkeletonViewport { Layout.fillWidth: true; Layout.fillHeight: true; service: parent.service; side: 1; visible: service.state.mode!=="Before"; overlay: service.state.mode==="Overlay" }
}
