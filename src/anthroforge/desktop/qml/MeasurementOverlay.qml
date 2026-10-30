import AnthroForge.Desktop 1.0
import QtQuick

Canvas {
    id: overlay
    required property var viewport
    readonly property var evidence: App.inspectionTools.state
    anchors.fill: parent
    function dot(ctx, point, label) {
        if(!viewport.pointInFront(point)) return null;
        const p=viewport.projectPoint(point[0],point[1],point[2]);
        ctx.beginPath(); ctx.arc(p.x,p.y,4,0,Math.PI*2); ctx.fill(); ctx.fillText(label,p.x+7,p.y-7);
        return p;
    }
    function ruler(ctx, first, second, text, stale) {
        if(!viewport.pointInFront(first) || !viewport.pointInFront(second)) return;
        ctx.strokeStyle=ctx.fillStyle=stale ? "#ffcc64" : "#7bdcff";
        const a=dot(ctx,first,"A"), b=dot(ctx,second,"B");
        ctx.setLineDash(stale ? [5,4] : []); ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
        ctx.fillText(text,(a.x+b.x)/2+5,(a.y+b.y)/2-8);
    }
    onEvidenceChanged: requestPaint()
    onPaint: {
        const ctx=getContext("2d"); ctx.reset(); ctx.lineWidth=2; ctx.font="12px sans-serif";
        for(const row of evidence.measurements) ruler(ctx,row.start.position,row.end.position,viewport.formatLength(row.distance),row.stale);
        ctx.fillStyle="#7bdcff";
        if(evidence.start.position) dot(ctx,evidence.start.position,"A");
        if(evidence.hover.position) dot(ctx,evidence.hover.position,evidence.start.position ? "B" : "A");
        if(evidence.start.position && evidence.hover.position) ruler(ctx,evidence.start.position,evidence.hover.position,"",false);
    }
    Connections { target: App.runtime; function onChanged() { overlay.requestPaint(); } }
}
