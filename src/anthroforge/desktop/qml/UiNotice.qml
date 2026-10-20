import QtQuick

QtObject {
    id: notice
    property string text: ""
    property bool active: true
    property bool error: false
    property int owner: 0
    readonly property string message: active ? text : ""
    onMessageChanged: if(owner) ToastBus.publish(owner,message,error)
    Component.onCompleted: { owner=ToastBus.allocate(); ToastBus.publish(owner,message,error); }
    Component.onDestruction: ToastBus.clear(owner)
}
