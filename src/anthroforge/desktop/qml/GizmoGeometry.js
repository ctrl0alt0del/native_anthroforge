.pragma library

function point(x, y) { return {x:x,y:y}; }
function subtract(a, b) { return point(a.x-b.x,a.y-b.y); }
function dot(a, b) { return a.x*b.x+a.y*b.y; }
function length(a) { return Math.sqrt(dot(a,a)); }
function along(a, b, t) { return point(a.x+b.x*t,a.y+b.y*t); }
function distance(a, b) { return length(subtract(a,b)); }
function segment(p, a, b) {
    const d=subtract(b,a), t=Math.max(0,Math.min(1,dot(subtract(p,a),d)/Math.max(1,dot(d,d))));
    return distance(p,along(a,d,t));
}
function basis(axis, quaternion) {
    const v=[0,0,0]; v[axis]=1;
    if (!quaternion) return v;
    const w=quaternion[0], q=quaternion.slice(1), t=cross(q,v).map(n=>n*2), u=cross(q,t);
    return v.map((n,i)=>n+w*t[i]+u[i]);
}
function cross(a,b) { return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]; }
function offset(center, direction, size) { return center.map((n,i)=>n+direction[i]*size); }
function geometry(project, center, size, mode, quaternion) {
    const origin=project(center[0],center[1],center[2]);
    const axes=[0,1,2].map(i=>{const p=offset(center,basis(i,mode==="Scale"?quaternion:null),size);return subtract(project(p[0],p[1],p[2]),origin);});
    const rings=mode==="Rotate"?[0,1,2].map(i=>ring(project,center,size,i)):[];
    return {center:origin,pivot:center,axes:axes,rings:rings,size:size,mode:mode};
}
function ring(project, center, size, axis) {
    const points=[], a=(axis+1)%3, b=(axis+2)%3;
    for(let i=0;i<=96;i++) {
        const p=center.slice(), angle=2*Math.PI*i/96;
        p[a]+=Math.cos(angle)*size; p[b]+=Math.sin(angle)*size;
        points.push(project(p[0],p[1],p[2]));
    }
    return points;
}
function plane(g, axis) {
    const a=g.axes[(axis+1)%3], b=g.axes[(axis+2)%3];
    return [[.23,.23],[.48,.23],[.48,.48],[.23,.48]].map(t=>along(along(g.center,a,t[0]),b,t[1]));
}
function coordinates(p,a,b) {
    const determinant=a.x*b.y-a.y*b.x;
    if(Math.abs(determinant)<40) return null;
    return [(p.x*b.y-p.y*b.x)/determinant,(a.x*p.y-a.y*p.x)/determinant];
}
function hitPlane(g,p) {
    for(let i=0;i<3;i++) {
        const uv=coordinates(subtract(p,g.center),g.axes[(i+1)%3],g.axes[(i+2)%3]);
        if(uv && uv.every(n=>n>=.18 && n<=.53)) return {kind:"plane",axis:i};
    }
    return null;
}
function hit(g,mode,p) {
    if(!g) return null;
    if(mode==="Rotate") return hitRing(g,p);
    if(distance(p,g.center)<12) return {kind:"center",axis:-1};
    const planeHit=mode==="Move"?hitPlane(g,p):null;
    if(planeHit) return planeHit;
    let best=null, nearest=11;
    for(let i=0;i<3;i++) {
        const d=segment(p,along(g.center,g.axes[i],.18),along(g.center,g.axes[i],1.06));
        if(length(g.axes[i])>18 && d<nearest) {nearest=d; best={kind:"axis",axis:i};}
    }
    return best;
}
function hitRing(g,p) {
    let best=null, nearest=9;
    for(let axis=0;axis<3;axis++) for(let i=1;i<g.rings[axis].length;i++) {
        const d=segment(p,g.rings[axis][i-1],g.rings[axis][i]);
        if(d<nearest) {nearest=d;best={kind:"ring",axis:axis,segment:i};}
    }
    return best;
}
function planeIntersection(g,axis,p,worldRay) {
    const ray=worldRay(p.x,p.y), direction=ray.direction[axis];
    if(Math.abs(direction)<0.025*Math.hypot(...ray.direction)) return null;
    const t=(g.pivot[axis]-ray.origin[axis])/direction;
    if(t<0) return null;
    return ray.origin.map((value,i)=>value+t*ray.direction[i]-g.pivot[i]);
}
function rotationAngle(g,axis,p,worldRay) {
    const position=planeIntersection(g,axis,p,worldRay);
    return position?Math.atan2(position[(axis+2)%3],position[(axis+1)%3]):null;
}
function rotationStep(drag,p,worldRay) {
    const angle=rotationAngle(drag.geometry,drag.hit.axis,p,worldRay);
    if(angle!==null && drag.angle!==null) {
        let change=angle-drag.angle;
        change=Math.atan2(Math.sin(change),Math.cos(change));
        drag.total+=change; drag.angle=angle;
    } else {
        const ring=drag.geometry.rings[drag.hit.axis], i=drag.hit.segment;
        const tangent=subtract(ring[i],ring[i-1]), delta=subtract(p,drag.start);
        drag.total=dot(delta,tangent)/Math.max(1,length(tangent))/80;
    }
    return drag.total*180/Math.PI;
}
function values(drag,p,precision,freeMove,worldRay) {
    const result=[0,0,0,0,0,0,1,1,1], hit=drag.hit, g=drag.geometry;
    const delta=subtract(p,drag.start), factor=precision ? 0.1 : 1;
    if(drag.mode==="Rotate") result[3+hit.axis]=rotationStep(drag,p,worldRay)*factor;
    else if(drag.mode==="Scale") scaleValues(result,drag,delta,factor);
    else moveValues(result,drag,delta,factor,freeMove);
    return result;
}
function scaleValues(result,drag,delta,factor) {
    const hit=drag.hit, axis=hit.axis>=0?drag.geometry.axes[hit.axis]:null;
    const amount=axis?dot(delta,axis)/Math.max(100,dot(axis,axis)):(delta.x-delta.y)/120;
    const scale=Math.max(.01,1+amount*factor);
    for(let i=0;i<3;i++) if(hit.kind==="center" || hit.axis===i) result[6+i]=scale;
}
function moveValues(result,drag,delta,factor,freeMove) {
    const hit=drag.hit,g=drag.geometry;
    if(hit.kind==="center") {const shift=freeMove(delta); for(let i=0;i<3;i++) result[i]=shift[i]*factor;return;}
    if(hit.kind==="axis") {
        const axis=g.axes[hit.axis]; result[hit.axis]=dot(delta,axis)/Math.max(100,dot(axis,axis))*g.size*factor;
    } else {
        const a=(hit.axis+1)%3,b=(hit.axis+2)%3,uv=coordinates(delta,g.axes[a],g.axes[b]);
        if(uv) {result[a]=uv[0]*g.size*factor;result[b]=uv[1]*g.size*factor;}
    }
}
