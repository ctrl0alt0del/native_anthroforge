// SPDX-License-Identifier: GPL-3.0-or-later
// Staged adapter of libigl outer_hull (Alec Jacobson, 2015, MPL-2.0).
// Keep exact arrangement coordinates until exterior-cell classification completes.
#include "exterior.hpp"
#include <igl/copyleft/cgal/remesh_self_intersections.h>
#include <igl/copyleft/cgal/extract_cells.h>
#include <igl/copyleft/cgal/assign.h>
#include <igl/remove_unreferenced.h>

namespace af::boolean {
using Exact=Eigen::Matrix<CGAL::Epeck::FT,Eigen::Dynamic,3,Eigen::RowMajor>;
struct Arrangement { Exact vertices; Triangles faces; Eigen::VectorXi origins; Eigen::MatrixXi cells; };
static void checkpoint(const std::atomic<bool>* cancel) {
    if(cancel&&cancel->load()) throw std::runtime_error("Calculation cancelled.");
}
static Arrangement arrange(const Vertices& v,const Triangles& f,const std::atomic<bool>* cancel) {
    Arrangement result; Eigen::MatrixXi intersections; Eigen::VectorXi mapping,unused;
    igl::copyleft::cgal::RemeshSelfIntersectionsParam settings; settings.stitch_all=true;
    checkpoint(cancel);
    igl::copyleft::cgal::remesh_self_intersections(v,f,settings,result.vertices,result.faces,intersections,result.origins,mapping);
    checkpoint(cancel);
    for(int i=0;i<result.faces.size();++i) result.faces.data()[i]=mapping[result.faces.data()[i]];
    igl::remove_unreferenced(Exact(result.vertices),Triangles(result.faces),result.vertices,result.faces,unused);
    igl::copyleft::cgal::extract_cells(result.vertices,result.faces,result.cells);
    checkpoint(cancel); return result;
}
static Exterior boundary(const Arrangement& source,const std::atomic<bool>* cancel) {
    std::vector<int> selected;
    for(int i=0;i<source.cells.rows();++i) if(source.cells(i,0)==0||source.cells(i,1)==0) selected.push_back(i);
    Exterior result; result.faces.resize(selected.size(),3); result.origins.resize(selected.size());
    for(size_t j=0;j<selected.size();++j) {
        checkpoint(cancel); const int i=selected[j];
        result.faces.row(j)=source.faces.row(i);
        if(source.cells(i,0)!=0) result.faces.row(j).reverseInPlace();
        result.origins[j]=source.origins[i];
    }
    Vertices rounded; Eigen::VectorXi unused;
    igl::copyleft::cgal::assign(source.vertices,rounded);
    igl::remove_unreferenced(rounded,Triangles(result.faces),result.vertices,result.faces,unused);
    checkpoint(cancel); return result;
}
Exterior exterior(const Vertices& vertices,const Triangles& faces,const std::atomic<bool>* cancel) {
    if(!faces.rows()) return {};
    return boundary(arrange(vertices,faces,cancel),cancel);
}
}
