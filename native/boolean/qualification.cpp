// SPDX-License-Identifier: GPL-3.0-or-later
#include "qualification.hpp"
#include <igl/copyleft/cgal/remesh_self_intersections.h>
#include <igl/copyleft/cgal/extract_cells.h>
#include <igl/is_edge_manifold.h>
#include <igl/is_vertex_manifold.h>
#include <array>
#include <algorithm>
#include <set>

namespace af::boolean {
using Kernel=CGAL::Exact_predicates_inexact_constructions_kernel;
using Exact=Eigen::Matrix<CGAL::Epeck::FT,Eigen::Dynamic,3,Eigen::RowMajor>;
static void checkpoint(const std::atomic<bool>* cancel) {
    if(cancel&&cancel->load()) throw std::runtime_error("Calculation cancelled.");
}
static bool unique_vertices(const Vertices& vertices,const std::atomic<bool>* cancel) {
    if(!vertices.allFinite()) return false;
    std::set<std::array<double,3>> seen;
    for(int i=0;i<vertices.rows();++i) {
        checkpoint(cancel);
        if(!seen.insert({vertices(i,0),vertices(i,1),vertices(i,2)}).second) return false;
    }
    return true;
}
static bool regular_triangle(const Vertices& vertices,const Eigen::RowVector3i& face) {
    std::array<Kernel::Point_3,3> points;
    for(int j=0;j<3;++j) points[size_t(j)]=Kernel::Point_3(vertices(face[j],0),vertices(face[j],1),vertices(face[j],2));
    const Eigen::Vector3d ab=vertices.row(face[1])-vertices.row(face[0]),ac=vertices.row(face[2])-vertices.row(face[0]);
    const Eigen::Vector3d normal=ab.cross(ac);
    return normal.allFinite()&&normal.squaredNorm()>0&&!CGAL::collinear(points[0],points[1],points[2]);
}
static bool regular_faces(const Vertices& vertices,const Triangles& faces,const std::atomic<bool>* cancel) {
    if(!faces.rows()||faces.minCoeff()<0||faces.maxCoeff()>=vertices.rows()) return false;
    std::set<std::array<int,3>> seen;
    for(int i=0;i<faces.rows();++i) {
        checkpoint(cancel); std::array<int,3> key{faces(i,0),faces(i,1),faces(i,2)};
        std::sort(key.begin(),key.end());
        if(!seen.insert(key).second||!regular_triangle(vertices,faces.row(i))) return false;
    }
    return igl::is_edge_manifold(faces)&&igl::is_vertex_manifold(faces);
}
static bool intersects(const Vertices& vertices,const Triangles& faces) {
    Vertices changed; Triangles triangles; Eigen::MatrixXi pairs; Eigen::VectorXi origins,mapping;
    const igl::copyleft::cgal::RemeshSelfIntersectionsParam settings(true,true);
    igl::copyleft::cgal::remesh_self_intersections(vertices,faces,settings,changed,triangles,pairs,origins,mapping);
    return pairs.rows()>0;
}
static Suitability exposed(const Vertices& vertices,const Triangles& faces,
    const std::vector<uint8_t>& selectable,const std::atomic<bool>* cancel) {
    const Exact exact=vertices.cast<CGAL::Epeck::FT>(); Eigen::MatrixXi cells;
    igl::copyleft::cgal::extract_cells(exact,faces,cells); checkpoint(cancel);
    for(int i=0;i<faces.rows();++i) if(selectable[size_t(i)]) {
        checkpoint(cancel);
        if(cells(i,0)!=0&&cells(i,1)!=0) return Suitability::Interior;
        if(cells(i,0)!=0) return Suitability::Orientation;
    }
    return Suitability::Reusable;
}
Suitability qualify(const Vertices& vertices,const Triangles& faces,
    const std::vector<uint8_t>& selectable,const std::atomic<bool>* cancel) {
    checkpoint(cancel);
    if(selectable.size()!=size_t(faces.rows())) throw std::runtime_error("Query face mask does not match geometry.");
    if(!unique_vertices(vertices,cancel)||!regular_faces(vertices,faces,cancel)) return Suitability::Topology;
    const bool crossing=intersects(vertices,faces); checkpoint(cancel);
    if(crossing) return Suitability::Intersections;
    return exposed(vertices,faces,selectable,cancel);
}
}
