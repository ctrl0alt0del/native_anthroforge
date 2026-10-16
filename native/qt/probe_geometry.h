#pragma once
#include <QtQuick3D/QQuick3DGeometry>
#include <QtQml/qqmlregistration.h>

/* Development render fixture, not an anatomical primitive or document object. */
class ProbeGeometry : public QQuick3DGeometry {
    Q_OBJECT
    QML_ELEMENT
public:
    explicit ProbeGeometry(QQuick3DObject* parent = nullptr);
};

