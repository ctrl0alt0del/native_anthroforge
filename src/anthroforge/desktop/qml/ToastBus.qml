pragma Singleton
import QtQuick

QtObject {
    id: bus
    property int serial: 0
    property int owner: 0
    property string text: ""
    property bool error: false
    property bool showing: false
    property Timer lifetime: Timer { interval: bus.error ? 8000 : 4500; onTriggered: bus.showing=false }
    function allocate() { serial+=1; return serial; }
    function publish(key, message, failure) {
        if(!message) { clear(key); return; }
        if(showing && error && !failure && owner!==key) return;
        owner=key; text=message.slice(0,600); error=failure; showing=true;
        lifetime.restart();
    }
    function clear(key) {
        if(owner!==key) return;
        showing=false; lifetime.stop();
    }
}
