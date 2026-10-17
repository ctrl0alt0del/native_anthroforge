.pragma library
.import "GizmoGeometry.js" as G

const colors=["#f47779","#7ed6a5","#79b7ff"];
function path(ctx, points, close) {
    ctx.beginPath(); ctx.moveTo(points[0].x,points[0].y);
    for(let i=1;i<points.length;i++) ctx.lineTo(points[i].x,points[i].y);
    if(close) ctx.closePath();
}
function highlighted(hit,kind,axis) { return hit && hit.kind===kind && hit.axis===axis; }
function draw(ctx,g,mode,hit) {
    ctx.lineJoin="round";ctx.lineCap="round";
    if(mode==="Rotate") {for(let i=0;i<3;i++) ring(ctx,g,i,hit); return;}
    if(mode==="Move") for(let i=0;i<3;i++) plane(ctx,g,i,hit);
    for(let i=0;i<3;i++) axis(ctx,g,i,mode,hit);
    ctx.strokeStyle=hit && hit.kind==="center"?"#ffffff":"#cfd2da";ctx.fillStyle="#343841";ctx.lineWidth=2;
    ctx.beginPath();
    if(mode==="Scale") ctx.rect(g.center.x-6,g.center.y-6,12,12);
    else ctx.arc(g.center.x,g.center.y,7,0,Math.PI*2);
    ctx.fill();ctx.stroke();
}
function ring(ctx,g,index,hit) {
    path(ctx,g.rings[index],false);ctx.lineWidth=5;ctx.strokeStyle="#22252ccc";ctx.stroke();
    ctx.lineWidth=highlighted(hit,"ring",index)?4:2.5;
    ctx.strokeStyle=highlighted(hit,"ring",index)?"#ffffff":colors[index];ctx.stroke();
}
function plane(ctx,g,index,hit) {
    const points=G.plane(g,index), area=G.coordinates(G.point(1,1),g.axes[(index+1)%3],g.axes[(index+2)%3]);
    if(!area) return;
    path(ctx,points,true);ctx.globalAlpha=.28;ctx.fillStyle=colors[index];ctx.fill();ctx.globalAlpha=1;
    ctx.lineWidth=1;ctx.strokeStyle=highlighted(hit,"plane",index)?"#ffffff":colors[index];ctx.stroke();
}
function axis(ctx,g,index,mode,hit) {
    const vector=g.axes[index], size=G.length(vector);
    if(size<18) return;
    const end=G.along(g.center,vector,1), start=G.along(g.center,vector,.14);
    path(ctx,[start,end],false);ctx.lineWidth=5;ctx.strokeStyle="#22252c";ctx.stroke();
    ctx.strokeStyle=highlighted(hit,"axis",index)?"#ffffff":colors[index];ctx.fillStyle=ctx.strokeStyle;ctx.lineWidth=2.5;ctx.stroke();
    if(mode==="Move") arrow(ctx,end,vector,size); else ctx.fillRect(end.x-5,end.y-5,10,10);
    const label=G.along(g.center,vector,1.18);ctx.font="bold 11px sans-serif";ctx.textAlign="center";ctx.fillText(["X","Y","Z"][index],label.x,label.y+4);
}
function arrow(ctx,end,vector,size) {
    const unit=G.point(vector.x/size,vector.y/size), back=G.along(end,unit,-13);
    path(ctx,[end,G.along(back,G.point(-unit.y,unit.x),5),G.along(back,G.point(-unit.y,unit.x),-5)],true);ctx.fill();
}
