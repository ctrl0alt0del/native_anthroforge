#pragma once
#include <QtQuick3D/QQuick3DGeometry>
#include <QtQml/qqmlregistration.h>

class ControlGeometry : public QQuick3DGeometry {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QVariantList points READ points WRITE setPoints NOTIFY changed)
    Q_PROPERTY(float radius READ radius WRITE setRadius NOTIFY changed)
    Q_PROPERTY(bool segments READ segments WRITE setSegments NOTIFY changed)
    Q_PROPERTY(float stroke READ stroke WRITE setStroke NOTIFY changed)
public:
    explicit ControlGeometry(QQuick3DObject* parent=nullptr): QQuick3DGeometry(parent) {}
    QVariantList points() const { return m_points; }
    float radius() const { return m_radius; }
    bool segments() const { return m_segments; }
    float stroke() const { return m_stroke; }
    void setStroke(float stroke);
    void setSegments(bool segments);
    void setPoints(const QVariantList& points);
    void setRadius(float radius);
signals:
    void changed();
private:
    QVariantList m_points;
    float m_radius=0.005f;
    bool m_segments=false;
    float m_stroke=0;
    void rebuild();
    void rebuildStroke();
    void appendStroke(QByteArray& data,const QVector3D& a,const QVector3D& b);
    void appendPoint(QByteArray& data,const QVector3D& point);
    void publish(const QByteArray& data,const QVector3D& low,const QVector3D& high);
};
