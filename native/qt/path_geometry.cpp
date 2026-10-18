#include "path_geometry.h"
#include <QtGui/QVector3D>
#include "anthroforge/path.h"

void PathGeometry::setAssetId(qulonglong value) {
    if(value==m_asset) return;
    m_asset=value; rebuild(); emit pathChanged();
}
void PathGeometry::setChunk(int value) {
    if(value==m_chunk) return;
    m_chunk=value; rebuild(); emit pathChanged();
}
void PathGeometry::rebuild() {
    clear();
    if(!m_asset) { update(); return; }
    const float* data=nullptr; int count=0; int64_t info[3]; double bounds[6];
    if(af_path_chunk(m_asset,m_chunk,&data,&count)||af_path_info(m_asset,info,bounds)) return;
    configure(QByteArray(reinterpret_cast<const char*>(data),count*sizeof(float)),bounds);
    update();
}
void PathGeometry::configure(const QByteArray& data,const double* bounds) {
    setVertexData(data);
    setStride(3*sizeof(float));
    setPrimitiveType(PrimitiveType::LineStrip);
    addAttribute(Attribute::PositionSemantic,0,Attribute::F32Type);
    setBounds(QVector3D(bounds[0],bounds[1],bounds[2]),QVector3D(bounds[3],bounds[4],bounds[5]));
}
