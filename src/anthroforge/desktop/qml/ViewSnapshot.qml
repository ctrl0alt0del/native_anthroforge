import QtQuick

QtObject {
    id: snapshot
    required property var source
    property var data: ({})
    function refresh() { data=source ? source.snapshot() : ({}); }
    property Connections updates: Connections {
        target: snapshot.source
        function onChanged() { snapshot.refresh(); }
    }
    onSourceChanged: refresh()
    Component.onCompleted: refresh()
}
