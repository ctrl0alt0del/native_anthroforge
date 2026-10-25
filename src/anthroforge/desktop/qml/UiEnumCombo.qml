import QtQuick

UiCombo {
    id: control
    property var codes: []
    property string value: ""
    signal chosen(string code)
    model: codes; enumLabels:true
    currentIndex: Math.max(0,codes.indexOf(value))
    onActivated: chosen(codes[currentIndex])
}
