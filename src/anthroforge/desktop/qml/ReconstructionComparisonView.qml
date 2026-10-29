import QtQuick
import QtQuick.Layouts

RowLayout {
    property var service: workspace.reconstructionCompare.comparison
    SkeletonViewport { Layout.fillWidth: true; Layout.fillHeight: true; service: parent.service; side: 0; visible: ["Split","Before"].includes(service.state.mode) }
    SkeletonViewport { Layout.fillWidth: true; Layout.fillHeight: true; service: parent.service; side: 1; visible: service.state.mode!=="Before"; overlay: service.state.mode==="Overlay" }
}
