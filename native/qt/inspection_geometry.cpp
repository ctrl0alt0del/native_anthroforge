#include "inspection_geometry.h"
#include "anthroforge/inspection.h"
#include <QtGui/QVector3D>

void InspectionGeometry::setAssetId(qulonglong value) {
    if(value==asset_) return;
    asset_=value; rebuild(); emit changed();
}
void InspectionGeometry::setChunk(int value) {
    if(value==chunk_) return;
    chunk_=value; rebuild(); emit changed();
}
void InspectionGeometry::rebuild() {
    clear(); if(!asset_) { update(); return; }
    const float* data=nullptr; int count=0; double values[10]; int64_t sizes[2];
    if(af_inspection_chunk(asset_,chunk_,&data,&count)||af_inspection_summary(asset_,values,sizes)) return;
    configure(QByteArray(reinterpret_cast<const char*>(data),count*sizeof(float)),values+4); update();
}
void InspectionGeometry::configure(const QByteArray& data,const double* bounds) {
    setVertexData(data); setStride(10*sizeof(float)); setPrimitiveType(PrimitiveType::Triangles);
    addAttribute(Attribute::PositionSemantic,0,Attribute::F32Type);
    addAttribute(Attribute::NormalSemantic,3*sizeof(float),Attribute::F32Type);
    addAttribute(Attribute::ColorSemantic,6*sizeof(float),Attribute::F32Type);
    setBounds(QVector3D(bounds[0],bounds[1],bounds[2]),QVector3D(bounds[3],bounds[4],bounds[5]));
}
