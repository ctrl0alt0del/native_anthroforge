#include "mesh_geometry.h"
#include "geometry_orientation.h"
#include <QtGui/QVector3D>
#include "anthroforge/mesh.h"

void MeshGeometry::setAssetId(qulonglong value) {
    if(value==m_asset) return;
    m_asset=value; rebuild(); emit meshChanged();
}
void MeshGeometry::setChunk(int value) {
    if(value==m_chunk) return;
    m_chunk=value; rebuild(); emit meshChanged();
}
void MeshGeometry::setReflected(bool value) {
    if(value==m_reflected) return;
    m_reflected=value; rebuild(); emit meshChanged();
}
void MeshGeometry::rebuild() {
    clear();
    if(!m_asset) { update(); return; }
    const float* data=nullptr; int count=0; double bounds[6];
    if(af_mesh_chunk(m_asset,m_chunk,&data,&count)||af_mesh_bounds(m_asset,bounds)) return;
    configure(QByteArray(reinterpret_cast<const char*>(data),count*sizeof(float)),bounds);
    update();
}
void MeshGeometry::configure(const QByteArray& data,const double* bounds) {
    setVertexData(data);
    setStride(6*sizeof(float));
    setPrimitiveType(PrimitiveType::Triangles);
    addAttribute(Attribute::PositionSemantic,0,Attribute::F32Type);
    addAttribute(Attribute::NormalSemantic,3*sizeof(float),Attribute::F32Type);
    reflected_indices(*this,data.size()/(6*sizeof(float)),m_reflected);
    setBounds(QVector3D(bounds[0],bounds[1],bounds[2]),QVector3D(bounds[3],bounds[4],bounds[5]));
}
