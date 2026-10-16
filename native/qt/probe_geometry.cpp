#include "probe_geometry.h"
#include "anthroforge/api.h"
#include <QtGui/QVector3D>
#include <array>

namespace {
const std::array<QVector3D, 6> points{{
    {-90, 0, 0}, {90, 0, 0}, {0, -130, 0},
    {0, 130, 0}, {0, 0, -65}, {0, 0, 65}
}};
const std::array<std::array<int, 3>, 8> faces{{
    {0, 3, 5}, {5, 3, 1}, {1, 3, 4}, {4, 3, 0},
    {5, 2, 0}, {1, 2, 5}, {4, 2, 1}, {0, 2, 4}
}};

void append_vertex(QByteArray& data, const QVector3D& p, const QVector3D& n) {
    const float values[]{p.x(), p.y(), p.z(), n.x(), n.y(), n.z()};
    data.append(reinterpret_cast<const char*>(values), sizeof(values));
}

QByteArray fixture_vertices() {
    QByteArray data;
    for (const auto& face : faces) {
        const auto a = points[face[0]], b = points[face[1]], c = points[face[2]];
        const auto normal = QVector3D::normal(a, b, c);
        append_vertex(data, a, normal);
        append_vertex(data, b, normal);
        append_vertex(data, c, normal);
    }
    return data;
}

std::array<double, 6> fixture_bounds() {
    std::array<double, 18> xyz{};
    for (size_t i = 0; i < points.size(); ++i) {
        xyz[i * 3] = points[i].x();
        xyz[i * 3 + 1] = points[i].y();
        xyz[i * 3 + 2] = points[i].z();
    }
    std::array<double, 6> bounds{};
    if (af_bounds3d(xyz.data(), points.size(), bounds.data()) != 0)
        qFatal("Invalid render fixture");
    return bounds;
}
}

ProbeGeometry::ProbeGeometry(QQuick3DObject* parent) : QQuick3DGeometry(parent) {
    const auto bounds = fixture_bounds();
    setVertexData(fixture_vertices());
    setStride(6 * sizeof(float));
    setPrimitiveType(PrimitiveType::Triangles);
    addAttribute(Attribute::PositionSemantic, 0, Attribute::F32Type);
    addAttribute(Attribute::NormalSemantic, 3 * sizeof(float), Attribute::F32Type);
    setBounds(QVector3D(bounds[0], bounds[1], bounds[2]),
              QVector3D(bounds[3], bounds[4], bounds[5]));
}

