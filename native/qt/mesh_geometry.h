#pragma once
#include <QtQuick3D/QQuick3DGeometry>
#include <QtQml/qqmlregistration.h>

class MeshGeometry: public QQuick3DGeometry {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(qulonglong assetId READ assetId WRITE setAssetId NOTIFY meshChanged)
    Q_PROPERTY(int chunk READ chunk WRITE setChunk NOTIFY meshChanged)
    Q_PROPERTY(bool reflected READ reflected WRITE setReflected NOTIFY meshChanged)
    Q_PROPERTY(int vertexCount READ vertexCount NOTIFY meshChanged)
public:
    explicit MeshGeometry(QQuick3DObject* parent=nullptr):QQuick3DGeometry(parent) {}
    qulonglong assetId() const { return m_asset; }
    int chunk() const { return m_chunk; }
    bool reflected() const { return m_reflected; }
    int vertexCount() const { return vertexData().size()/(6*sizeof(float)); }
    void setAssetId(qulonglong value);
    void setChunk(int value);
    void setReflected(bool value);
signals:
    void meshChanged();
private:
    void rebuild();
    void configure(const QByteArray& data,const double* bounds);
    void orientation(int count);
    qulonglong m_asset=0;
    int m_chunk=0;
    bool m_reflected=false;
};
