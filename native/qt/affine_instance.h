#pragma once
#include <QtQuick3D/QQuick3DInstancing>
#include <QtQml/qqmlregistration.h>
#include <QtCore/QVariantList>

// One full affine matrix: ordinary nonuniform parenting must not lose shear to TRS.
class AffineInstance: public QQuick3DInstancing {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QVariantList frame READ frame WRITE setFrame NOTIFY frameChanged)
public:
    explicit AffineInstance(QQuick3DObject* parent=nullptr):QQuick3DInstancing(parent) {}
    QVariantList frame() const { return m_frame; }
    void setFrame(const QVariantList& values);
signals:
    void frameChanged();
protected:
    QByteArray getInstanceBuffer(int* count) override;
private:
    QVariantList m_frame;
    QByteArray m_buffer;
};
