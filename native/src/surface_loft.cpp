// SPDX-License-Identifier: GPL-3.0-or-later
#include "curve_surface_internal.hpp"
#include "material_domain.hpp"

namespace af::curve_surface {
static size_t row_count(const Rows& rows,const int* across) {
    size_t count=rows.size();
    for(size_t i=1;i<rows.size();++i) {
        if(across[i-1]<0||across[i-1]>int(max_vertices)) throw std::runtime_error("Invalid surface row density.");
        count+=size_t(across[i-1]);
    }
    return count;
}
static void append_rows(Points& points,const Row& a,const Row& b,int count,uint64_t cancel) {
    for(int i=0;i<count;++i) {
        const double t=double(i)/count;
        for(size_t j=0;j<a.points.size();++j) {
            check_cancel(cancel); points.push_back((1-t)*a.points[j]+t*b.points[j]);
        }
    }
}
static void material_axes(Mesh& mesh,const Rows& rows,int count,bool closed) {
    if(rows.front().material_stations.empty()) return;
    for(int i=0;i<count;++i) mesh.material_axes.push_back(double(i)/(count-int(!closed)));
    const auto& along=rows.front().material_stations;
    mesh.material_axes.insert(mesh.material_axes.end(),along.begin(),along.end());
}
std::shared_ptr<Mesh> loft(const Rows& rows,const int* across,bool close_across,bool flip,uint64_t cancel) {
    if(rows.size()<2||!across) throw std::runtime_error("Loft requires at least two source curves.");
    const size_t count=row_count(rows,across),columns=rows.front().points.size();
    budget(count*columns,2*count*columns);
    Points points; points.reserve(count*columns);
    for(size_t i=1;i<rows.size();++i) append_rows(points,rows[i-1],rows[i],across[i-1]+1,cancel);
    points.insert(points.end(),rows.back().points.begin(),rows.back().points.end());
    auto faces=grid_faces(int(count),int(columns),rows.front().closed,close_across&&count>2);
    if(flip) for(auto& face:faces) std::reverse(face.begin()+1,face.end());
    auto result=make_mesh(points,faces,cancel,false);
    result->material=grid_material(int(count),int(columns),rows.front().closed,close_across&&count>2);
    material_axes(*result,rows,int(count),close_across&&count>2);
    return result;
}
}
