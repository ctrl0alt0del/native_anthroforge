#pragma once
#include <QtQuick3D/QQuick3DTextureData>
#include <QtQml/qqmlregistration.h>

class ImageTexture: public QQuick3DTextureData {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(qulonglong assetId READ assetId WRITE setAssetId NOTIFY imageChanged)
    Q_PROPERTY(int tile READ tile WRITE setTile NOTIFY imageChanged)
public:
    explicit ImageTexture(QQuick3DObject* parent=nullptr):QQuick3DTextureData(parent) {}
    qulonglong assetId() const { return m_asset; }
    int tile() const { return m_tile; }
    void setAssetId(qulonglong value);
    void setTile(int value);
signals:
    void imageChanged();
private:
    void rebuild();
    qulonglong m_asset=0;
    int m_tile=0;
};
