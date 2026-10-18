#include "image_texture.h"
#include <QtCore/QSize>
#include "anthroforge/image.h"

void ImageTexture::setAssetId(qulonglong value) {
    if(value==m_asset) return;
    m_asset=value; rebuild(); emit imageChanged();
}
void ImageTexture::setTile(int value) {
    if(value==m_tile) return;
    m_tile=value; rebuild(); emit imageChanged();
}
void ImageTexture::rebuild() {
    const unsigned char* data=nullptr; int info[4];
    if(!m_asset||af_image_tile(m_asset,m_tile,&data,info)) return;
    setSize(QSize(info[2],info[3]));
    setFormat(QQuick3DTextureData::RGBA8);
    setHasTransparency(true);
    setTextureData(QByteArray(reinterpret_cast<const char*>(data),info[2]*info[3]*4));
}
