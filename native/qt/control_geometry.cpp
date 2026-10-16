#include "control_geometry.h"
#include <QtGui/QVector3D>

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
    for(int axis=0;axis<3;++axis) for(int sign:{-1,1}) {
        QVector3D p=point; p[axis]+=m_radius*sign;
        const float xyz[3]={p.x(),p.y(),p.z()};
        data.append(reinterpret_cast<const char*>(xyz),sizeof(xyz));
    }
}
void ControlGeometry::rebuild() {
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
    setVertexData(data); setStride(3*sizeof(float)); setPrimitiveType(PrimitiveType::Lines);
    addAttribute(Attribute::PositionSemantic,0,Attribute::F32Type);
    if(!m_points.isEmpty()) setBounds(low,high);
    update();
}
