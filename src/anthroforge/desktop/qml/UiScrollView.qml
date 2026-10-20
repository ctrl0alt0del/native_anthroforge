import QtQuick
import QtQuick.Controls

ScrollView {
    id: control
    clip: true
    contentWidth: availableWidth
    // Reserve the gutter even when content fits; calculation feedback cannot narrow fields.
    rightPadding: ScrollBar.vertical.implicitWidth + 4
    ScrollBar.vertical.policy: control.contentHeight > control.availableHeight ? ScrollBar.AlwaysOn : ScrollBar.AlwaysOff
}
