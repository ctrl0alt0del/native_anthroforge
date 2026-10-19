#include "affine_instance.h"
#include <QtGui/QVector4D>
#include <cmath>

static QVector4D matrix_row(const QVariantList& values,int row) {
    return QVector4D(values[row*4].toFloat(),values[row*4+1].toFloat(),
                     values[row*4+2].toFloat(),values[row*4+3].toFloat());
}
void AffineInstance::setFrame(const QVariantList& values) {
    if(values==m_frame) return;
    if(values.size()!=16) return;
    for(const auto& value:values) if(!std::isfinite(value.toFloat())) return;
    m_frame=values;
    const InstanceTableEntry entry{matrix_row(values,0),matrix_row(values,1),matrix_row(values,2),
        QVector4D(1,1,1,1),QVector4D()};
    m_buffer=QByteArray(reinterpret_cast<const char*>(&entry),sizeof(entry));
    markDirty(); emit frameChanged();
}
QByteArray AffineInstance::getInstanceBuffer(int* count) {
    *count=m_buffer.isEmpty()?0:1; return m_buffer;
}
