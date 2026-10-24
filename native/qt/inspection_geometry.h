#pragma once
#include <QtQuick3D/QQuick3DGeometry>
#include <QtQml/qqmlregistration.h>

class InspectionGeometry: public QQuick3DGeometry {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(qulonglong assetId READ assetId WRITE setAssetId NOTIFY changed)
    Q_PROPERTY(int chunk READ chunk WRITE setChunk NOTIFY changed)
    Q_PROPERTY(bool reflected READ reflected WRITE setReflected NOTIFY changed)
public:
    explicit InspectionGeometry(QQuick3DObject* parent=nullptr):QQuick3DGeometry(parent) {}
    qulonglong assetId() const { return asset_; }
    int chunk() const { return chunk_; }
    bool reflected() const { return reflected_; }
    void setAssetId(qulonglong value);
    void setChunk(int value);
    void setReflected(bool value);
signals:
    void changed();
private:
    void rebuild();
    void configure(const QByteArray& data,const double* bounds);
    qulonglong asset_=0;
    int chunk_=0;
    bool reflected_=false;
};
