#pragma once
#include <QtQuick3D/QQuick3DGeometry>

inline void reflected_indices(QQuick3DGeometry& geometry,int count,bool reflected) {
    if(!reflected) return;
    QByteArray indices(count*sizeof(quint32),Qt::Uninitialized);
    auto* output=reinterpret_cast<quint32*>(indices.data());
    for(int i=0;i<count;i+=3) {
        output[i]=i; output[i+1]=i+2; output[i+2]=i+1;
    }
    geometry.setIndexData(indices);
    geometry.addAttribute(QQuick3DGeometry::Attribute::IndexSemantic,0,
                          QQuick3DGeometry::Attribute::U32Type);
}
