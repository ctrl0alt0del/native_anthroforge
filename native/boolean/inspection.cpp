// SPDX-License-Identifier: GPL-3.0-or-later
#include "qualification.hpp"
#include <CGAL/Surface_mesh.h>
#include <CGAL/Side_of_triangle_mesh.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

namespace af::boolean {
using Kernel=CGAL::Exact_predicates_inexact_constructions_kernel;
using Surface=CGAL::Surface_mesh<Kernel::Point_3>;
static void checkpoint(const std::atomic<bool>* cancel) {
    if(cancel&&cancel->load()) throw std::runtime_error("Calculation cancelled.");
}
static Surface surface(const Vertices& vertices,const Triangles& triangles,const std::atomic<bool>* cancel) {
    Surface result; std::vector<Surface::Vertex_index> ids;
    for(int i=0;i<vertices.rows();++i) { checkpoint(cancel); ids.push_back(result.add_vertex({vertices(i,0),vertices(i,1),vertices(i,2)})); }
    for(int i=0;i<triangles.rows();++i) {
        checkpoint(cancel); const auto face=result.add_face(ids[size_t(triangles(i,0))],ids[size_t(triangles(i,1))],ids[size_t(triangles(i,2))]);
        if(face==Surface::null_face()) return {};
    }
    return result;
}
int classify(const Vertices& vertices,const Triangles& triangles,const Vertices& points,std::vector<int>& sides,const std::atomic<bool>* cancel) {
    checkpoint(cancel);
    const auto qualified=qualify(vertices,triangles,std::vector<uint8_t>(size_t(triangles.rows()),1),cancel);
    if(qualified!=Suitability::Reusable) return 2+int(qualified);
    const auto mesh=surface(vertices,triangles,cancel);
    if(mesh.is_empty()||!CGAL::is_closed(mesh)) return 1;
    const CGAL::Side_of_triangle_mesh<Surface,Kernel> inside(mesh); sides.clear(); sides.reserve(size_t(points.rows()));
    for(int i=0;i<points.rows();++i) { checkpoint(cancel); sides.push_back(int(inside({points(i,0),points(i,1),points(i,2)}))); }
    return 0;
}
}
