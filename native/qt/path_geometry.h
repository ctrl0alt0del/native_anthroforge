#pragma once
#include <QtQuick3D/QQuick3DGeometry>
#include <QtQml/qqmlregistration.h>

class PathGeometry: public QQuick3DGeometry {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(qulonglong assetId READ assetId WRITE setAssetId NOTIFY pathChanged)
    Q_PROPERTY(int chunk READ chunk WRITE setChunk NOTIFY pathChanged)
public:
    explicit PathGeometry(QQuick3DObject* parent=nullptr):QQuick3DGeometry(parent) {}
    qulonglong assetId() const { return m_asset; }
    int chunk() const { return m_chunk; }
    void setAssetId(qulonglong value);
    void setChunk(int value);
signals:
    void pathChanged();
private:
    void rebuild();
    void configure(const QByteArray& data,const double* bounds);
    qulonglong m_asset=0;
    int m_chunk=0;
};
