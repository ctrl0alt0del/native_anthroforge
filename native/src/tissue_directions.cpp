// SPDX-License-Identifier: GPL-3.0-or-later
// Screened diffusion of unit normals over physical surface distance (M + h²K).
// Unlike index-neighbour differences, this accounts for irregular sample areas.
#include "tissue_directions.hpp"
#include <Eigen/SparseCholesky>
#include <igl/cotmatrix.h>
#include <igl/massmatrix.h>

namespace af::tissue {
using Sparse=Eigen::SparseMatrix<double>;
static std::shared_ptr<Mesh> direction_domain(const Mesh& source,const MaterialGrid& grid,uint64_t cancel) {
    Points points;
    for(auto id:grid.indices) { check_cancel(cancel); points.push_back(source.vertices.row(id)); }
    return make_mesh(points,grid_faces(grid.rows,grid.columns,grid.closed_u,grid.closed_v),cancel,false);
}
static Vertices unit_normals(const Mesh& mesh,uint64_t cancel) {
    Vertices normals=Vertices::Zero(mesh.vertices.rows(),3);
    for(int i=0;i<mesh.triangles.rows();++i) {
        check_cancel(cancel); const auto t=mesh.triangles.row(i);
        const V3 a=mesh.vertices.row(t[1])-mesh.vertices.row(t[0]),b=mesh.vertices.row(t[2])-mesh.vertices.row(t[0]);
        const V3 normal=a.cross(b);
        for(int j=0;j<3;++j) normals.row(t[j])+=normal;
    }
    for(int i=0;i<normals.rows();++i) normals.row(i).normalize();
    return normals;
}
static Vertices diffuse(const Mesh& mesh,const Vertices& normals,double distance,uint64_t cancel) {
    Sparse stiffness,mass;
    igl::cotmatrix(mesh.vertices,mesh.triangles,stiffness);
    igl::massmatrix(mesh.vertices,mesh.triangles,igl::MASSMATRIX_TYPE_BARYCENTRIC,mass);
    check_cancel(cancel);
    Eigen::SimplicialLDLT<Sparse> solver(mass-distance*distance*stiffness);
    if(solver.info()!=Eigen::Success) throw std::runtime_error("Inflation direction system is singular.");
    Vertices result=solver.solve(mass*normals);
    if(solver.info()!=Eigen::Success||!result.allFinite()) throw std::runtime_error("Inflation direction solve failed.");
    check_cancel(cancel); return result;
}
Vertices inflation_directions(const Mesh& source,const MaterialGrid& grid,double distance,uint64_t cancel) {
    const auto domain=direction_domain(source,grid,cancel);
    auto result=diffuse(*domain,unit_normals(*domain,cancel),distance,cancel);
    for(int i=0;i<result.rows();++i) {
        check_cancel(cancel);
        if(result.row(i).norm()<1e-12) throw std::runtime_error("Inflation direction is undefined on this material surface.");
        result.row(i).normalize();
    }
    return result;
}
}
