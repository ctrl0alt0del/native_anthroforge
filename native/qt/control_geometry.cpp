#include "control_geometry.h"
#include <QtGui/QVector3D>

static QVector3D coordinate(const QVariant& value) {
    const auto row=value.toList();
    return {row.value(0).toFloat(),row.value(1).toFloat(),row.value(2).toFloat()};
}
static void appendQuad(QByteArray& data,const QVector3D& a,const QVector3D& b,
                       const QVector3D& c,const QVector3D& d) {
    for(const auto& p:{a,b,c,a,c,d}) {
        const float xyz[3]={p.x(),p.y(),p.z()};
        data.append(reinterpret_cast<const char*>(xyz),sizeof(xyz));
    }
}
void ControlGeometry::setStroke(float stroke) {
    if(m_stroke==stroke) return;
    m_stroke=stroke; rebuild(); emit changed();
}

void ControlGeometry::setPoints(const QVariantList& points) {
    if(m_points==points) return;
    m_points=points;
    rebuild();
    emit changed();
}
void ControlGeometry::setRadius(float radius) {
    if(m_radius==radius) return;
    m_radius=radius;
    rebuild();
    emit changed();
}
void ControlGeometry::setSegments(bool segments) {
    if(m_segments==segments) return;
    m_segments=segments; rebuild(); emit changed();
}
void ControlGeometry::appendPoint(QByteArray& data,const QVector3D& point) {
    for(int x:{-1,1}) for(int y:{-1,1}) for(int z:{-1,1}) {
        const int signs[3]={x,y,z};
        for(int axis=0;axis<3;++axis) {
            QVector3D p=point; p[axis]+=m_radius*signs[axis];
            const float xyz[3]={p.x(),p.y(),p.z()};
            data.append(reinterpret_cast<const char*>(xyz),sizeof(xyz));
        }
    }
}
void ControlGeometry::rebuild() {
    if(m_segments&&m_stroke>0) { rebuildStroke(); return; }
    clear(); QByteArray data; QVector3D low(1e20f,1e20f,1e20f),high(-1e20f,-1e20f,-1e20f);
    for(const auto& value:m_points) {
        const auto row=value.toList(); if(row.size()!=3) continue;
        const QVector3D p(row[0].toFloat(),row[1].toFloat(),row[2].toFloat());
        if(m_segments) {
            const float xyz[3]={p.x(),p.y(),p.z()};
            data.append(reinterpret_cast<const char*>(xyz),sizeof(xyz));
        } else appendPoint(data,p);
        for(int a=0;a<3;++a) { low[a]=qMin(low[a],p[a]-m_radius); high[a]=qMax(high[a],p[a]+m_radius); }
    }
    publish(data,low,high);
}
void ControlGeometry::appendStroke(QByteArray& data,const QVector3D& a,const QVector3D& b) {
    if((b-a).lengthSquared()<1e-20f) return;
    const QVector3D direction=(b-a).normalized();
    const QVector3D axis=qAbs(direction.z())<0.9f?QVector3D(0,0,1):QVector3D(0,1,0);
    const QVector3D side=QVector3D::crossProduct(direction,axis).normalized()*m_stroke;
    const QVector3D up=QVector3D::crossProduct(direction,side);
    const QVector3D ring[4]={side,up,-side,-up};
    for(int i=0;i<4;++i) {
        const int j=(i+1)%4;
        appendQuad(data,a+ring[i],b+ring[i],b+ring[j],a+ring[j]);
    }
}
void ControlGeometry::rebuildStroke() {
    clear(); QByteArray data; QVector3D low(1e20f,1e20f,1e20f),high(-1e20f,-1e20f,-1e20f);
    for(int i=0;i+1<m_points.size();i+=2) {
        const QVector3D a=coordinate(m_points[i]),b=coordinate(m_points[i+1]);
        appendStroke(data,a,b);
        for(int axis=0;axis<3;++axis) {
            low[axis]=qMin(low[axis],qMin(a[axis],b[axis])-m_stroke);
            high[axis]=qMax(high[axis],qMax(a[axis],b[axis])+m_stroke);
        }
    }
    publish(data,low,high);
}
void ControlGeometry::publish(const QByteArray& data,const QVector3D& low,const QVector3D& high) {
    setVertexData(data); setStride(3*sizeof(float));
    setPrimitiveType(m_segments&&m_stroke==0?PrimitiveType::Lines:PrimitiveType::Triangles);
    addAttribute(Attribute::PositionSemantic,0,Attribute::F32Type);
    if(!m_points.isEmpty()) setBounds(low,high);
    update();
}
