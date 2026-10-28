import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    property var evidence: []
    property int axis: 0
    readonly property var rows: flatten(evidence)
    function flatten(values) {
        let result=[];
        values.forEach(e=>(e.after || []).forEach((p,i)=>result.push({before:e.before[i]?.position || [],after:p.position || [],label:p.point})));
        return result;
    }
    RowLayout {
        Label { text: "Attachment locations · metres"; color: Theme.text; Layout.fillWidth: true }
        UiCombo { model: ["XY","XZ","YZ"]; onActivated: index=>panel.axis=index; implicitWidth: 70 }
    }
    Canvas {
        id: preview
        Layout.fillWidth: true; Layout.preferredHeight: 120
        onWidthChanged: requestPaint()
        Connections { target: panel; function onRowsChanged() { preview.requestPaint(); } function onAxisChanged() { preview.requestPaint(); } }
        function points() {
            const axes=[[0,1],[0,2],[1,2]][panel.axis];
            let rows=[]; panel.rows.forEach(r=>rows.push(r.before,r.after));
            return rows.filter(p=>p.length===3).map(p=>[p[axes[0]],p[axes[1]]]);
        }
        onPaint: {
            const c=getContext("2d"), p=points(); c.clearRect(0,0,width,height);
            if(!p.length) return;
            const xs=p.map(v=>v[0]), ys=p.map(v=>v[1]), x=Math.min(...xs), y=Math.min(...ys);
            const s=Math.min((width-24)/Math.max(.001,Math.max(...xs)-x),(height-24)/Math.max(.001,Math.max(...ys)-y));
            p.forEach((v,i)=>{ c.fillStyle=i%2 ? "#69bff0" : "#e9ad62"; c.beginPath(); c.arc(12+(v[0]-x)*s,height-12-(v[1]-y)*s,4,0,2*Math.PI); c.fill(); });
        }
    }
    Label { text: "Orange: original · Blue: proposed"; color: Theme.muted; font.pixelSize: 10 }
    ListView {
        Layout.fillWidth: true; Layout.preferredHeight: 70; clip: true
        model: panel.rows; ScrollBar.vertical: ScrollBar {}
        delegate: Label {
            required property var modelData
            width: ListView.view.width; color: Theme.muted; font.pixelSize: 10
            text: modelData.before.map(n=>n.toFixed(4)).join(", ")+" → "+modelData.after.map(n=>n.toFixed(4)).join(", ")
        }
    }
}
