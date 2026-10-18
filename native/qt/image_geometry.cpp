#include "image_geometry.h"
#include <QtGui/QVector3D>
#include <QtGui/QMatrix4x4>
#include "anthroforge/image.h"

void ImageGeometry::setAssetId(qulonglong value) {
    if(value==m_asset) return;
    m_asset=value; rebuild(); emit geometryChanged();
}
void ImageGeometry::setTile(int value) {
    if(value==m_tile) return;
    m_tile=value; rebuild(); emit geometryChanged();
}
void ImageGeometry::setDimensions(QSizeF value) {
    if(value==m_dimensions) return;
    m_dimensions=value; rebuild(); emit geometryChanged();
}
void ImageGeometry::setFrame(const QVariantList& value) {
    if(value==m_frame||value.size()!=16) return;
    m_frame=value; rebuild(); emit geometryChanged();
}
static QMatrix4x4 image_frame(const QVariantList& frame) {
    if(frame.size()!=16) return QMatrix4x4();
    float values[16];
    for(int i=0;i<16;++i) values[i]=frame[i].toFloat();
    return QMatrix4x4(values);
}
static std::pair<QVector3D,QVector3D> transform_quad(float* vertices,const QMatrix4x4& frame) {
    const QVector3D normal=QVector3D::crossProduct(frame.mapVector(QVector3D(1,0,0)),frame.mapVector(QVector3D(0,1,0))).normalized();
    QVector3D low,high;
    for(int i=0;i<6;++i) {
        const QVector3D p=frame.map(QVector3D(vertices[i*8],vertices[i*8+1],vertices[i*8+2]));
        if(i==0) low=high=p;
        for(int axis=0;axis<3;++axis) {
            low[axis]=std::min(low[axis],p[axis]); high[axis]=std::max(high[axis],p[axis]);
            vertices[i*8+axis]=p[axis]; vertices[i*8+axis+3]=normal[axis];
        }
    }
    return {low,high};
}
void ImageGeometry::rebuild() {
    float vertices[48];
    if(!m_asset||af_image_vertices(m_asset,m_tile,m_dimensions.width(),m_dimensions.height(),vertices)) return;
    const auto bounds=transform_quad(vertices,image_frame(m_frame));
    configure(vertices); setBounds(bounds.first,bounds.second); update();
}
void ImageGeometry::configure(float* vertices) {
    clear(); setPrimitiveType(QQuick3DGeometry::PrimitiveType::Triangles); setStride(8*sizeof(float));
    setVertexData(QByteArray(reinterpret_cast<const char*>(vertices),48*sizeof(float)));
    addAttribute(QQuick3DGeometry::Attribute::PositionSemantic,0,QQuick3DGeometry::Attribute::F32Type);
    addAttribute(QQuick3DGeometry::Attribute::NormalSemantic,3*sizeof(float),QQuick3DGeometry::Attribute::F32Type);
    addAttribute(QQuick3DGeometry::Attribute::TexCoordSemantic,6*sizeof(float),QQuick3DGeometry::Attribute::F32Type);
}
