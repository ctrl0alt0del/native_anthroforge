#pragma once
#include "anthroforge/mesh.h"
#include "tissue_domain.hpp"
#if defined(__GNUC__) && !defined(__clang__)
#pragma GCC diagnostic push
// Eigen's FromTwoVectors computes full V before reading its SVD nullspace.
// GCC 13 misdiagnoses that template path; keep the exception inside Eigen.
#pragma GCC diagnostic ignored "-Wmaybe-uninitialized"
#endif
#include <Eigen/Core>
#include <Eigen/Geometry>
#if defined(__GNUC__) && !defined(__clang__)
#pragma GCC diagnostic pop
#endif
#include <igl/AABB.h>
#include <atomic>
#include <memory>
#include <vector>
#include <string>

namespace af {
using V3 = Eigen::Vector3d;
using M3 = Eigen::Matrix3d;
using M4 = Eigen::Matrix<double,4,4,Eigen::RowMajor>;
using Vertices = Eigen::Matrix<double,Eigen::Dynamic,3,Eigen::RowMajor>;
using Triangles = Eigen::Matrix<int,Eigen::Dynamic,3,Eigen::RowMajor>;
using Faces = std::vector<std::vector<int64_t>>;
struct Mesh {
    bool generated=false;
    bool prepared=false;
    Vertices vertices;
    Triangles triangles;
    std::vector<int64_t> corners, offsets, polygons;
    std::vector<int64_t> material;
    std::vector<double> material_axes;
    std::vector<double> material_pins;
    TissueDomain tissue;
    std::vector<std::vector<float>> chunks;
    igl::AABB<Vertices,3> tree;
    double bounds[6]{};
};
struct Surface {
    Vertices vertices;
    const Triangles* triangles;
    igl::AABB<Vertices,3> tree;
    Surface(const Mesh& mesh, const M4& matrix);
};
struct Hit { int triangle=-1; V3 point=V3::Zero(), weights=V3::Zero(); double distance=0; };
struct Cancellation { std::atomic<bool> cancelled{false}; };
std::shared_ptr<Mesh> mesh(uint64_t handle);
uint64_t retain(std::shared_ptr<Mesh> mesh);
uint64_t mesh_storage(const Mesh& mesh);
std::shared_ptr<Mesh> read_mesh(const std::string& path, double units, bool y_up, uint64_t cancel);
void prepare_mesh(Mesh& mesh, const Faces& faces, uint64_t cancel=0,bool complete=true);
void set_error(const std::string& message);
void check_cancel(uint64_t token);
V3 point(const M4& matrix, const V3& value);
M4 geometry_matrix(const double* matrix, const double* offset);
M3 rotation(const M4& matrix);
V3 scales(const M4& matrix);
Hit nearest(const Surface& surface, const V3& point);
int pick_surface(const Mesh& mesh,const M4& world,const V3& origin,const V3& direction,double* output);
bool intersect_ray(const Mesh& mesh,const V3& origin,const V3& ray,igl::Hit& hit);
V3 barycentric(const V3& point, const V3& a, const V3& b, const V3& c);
}
