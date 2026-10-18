import QtQuick
import QtQuick.Controls

ScrollView {
    id: control
    clip: true
    contentWidth: availableWidth
    rightPadding: effectiveScrollBarWidth > 0 ? effectiveScrollBarWidth + 4 : 0
    ScrollBar.vertical.policy: control.contentHeight > control.availableHeight ? ScrollBar.AlwaysOn : ScrollBar.AlwaysOff
}
