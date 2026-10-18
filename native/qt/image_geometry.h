#pragma once
#include <QtCore/QSizeF>
#include <QtCore/QVariantList>
#include <QtQuick3D/QQuick3DGeometry>
#include <QtQml/qqmlregistration.h>

class ImageGeometry : public QQuick3DGeometry {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(qulonglong assetId READ assetId WRITE setAssetId NOTIFY geometryChanged)
    Q_PROPERTY(int tile READ tile WRITE setTile NOTIFY geometryChanged)
    Q_PROPERTY(QSizeF dimensions READ dimensions WRITE setDimensions NOTIFY geometryChanged)
    Q_PROPERTY(QVariantList frame READ frame WRITE setFrame NOTIFY geometryChanged)
public:
    explicit ImageGeometry(QQuick3DObject* parent=nullptr) : QQuick3DGeometry(parent) {}
    qulonglong assetId() const { return m_asset; }
    int tile() const { return m_tile; }
    QSizeF dimensions() const { return m_dimensions; }
    QVariantList frame() const { return m_frame; }
    void setAssetId(qulonglong value);
    void setTile(int value);
    void setDimensions(QSizeF value);
    void setFrame(const QVariantList& value);
signals:
    void geometryChanged();
private:
    void rebuild();
    void configure(float* vertices);
    qulonglong m_asset=0;
    int m_tile=0;
    QSizeF m_dimensions{1,1};
    QVariantList m_frame;
};
