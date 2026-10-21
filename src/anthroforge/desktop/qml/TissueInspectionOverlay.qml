import QtQuick

Canvas {
    id: overlay
    required property var viewport
    ViewSnapshot { id: evidence; source: workspace.tissueInspection }
    readonly property var lines: (evidence.data.lines || []).concat(evidence.data.footprint || [])
    anchors.fill: parent
    visible: lines.length > 0
    function segment(ctx, a, b) {
        if(!viewport.pointInFront(a) || !viewport.pointInFront(b)) return;
        const p=viewport.projectPoint(...a), q=viewport.projectPoint(...b);
        ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(q.x,q.y); ctx.stroke();
    }
    onLinesChanged: requestPaint()
    onPaint: {
        const ctx=getContext("2d"); ctx.reset(); ctx.lineWidth=1.5;
        ctx.strokeStyle=ctx.fillStyle="#ffe571"; ctx.setLineDash([4,3]);
        for(let i=0;i+1<lines.length;i+=2) segment(ctx,lines[i],lines[i+1]);
        ctx.font="12px sans-serif"; ctx.fillText("Tissue inspection · x-ray guides",12,54);
    }
    Connections {
        target: overlay.viewport
        function onCameraStateChanged() { overlay.requestPaint(); }
        function onDistanceChanged() { overlay.requestPaint(); }
        function onWidthChanged() { overlay.requestPaint(); }
        function onHeightChanged() { overlay.requestPaint(); }
    }
}
