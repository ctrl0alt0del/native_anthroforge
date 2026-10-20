// SPDX-License-Identifier: GPL-3.0-or-later
#include "material_chart.hpp"
#include <igl/point_mesh_squared_distance.h>

namespace af::material {
static void build(ChartIndex& target,const std::vector<M3>& source) {
    target.vertices.resize(source.size()*3,3); target.triangles.resize(source.size(),3);
    for(size_t i=0;i<source.size();++i) {
        target.vertices.middleRows<3>(int(i)*3)=source[i];
        target.triangles.row(int(i))=Eigen::Vector3i(int(i)*3,int(i)*3+1,int(i)*3+2);
    }
    if(!source.empty()) target.tree.init(target.vertices,target.triangles);
}
Indices indexed(const Mesh& mesh,const Atlas& atlas,uint64_t cancel) {
    Indices result; std::vector<std::vector<M3>> values(atlas.charts.size());
    for(size_t i=0;i<atlas.charts.size();++i) result.push_back(std::make_unique<ChartIndex>());
    for(int i=0;i<mesh.triangles.rows();++i) {
        check_cancel(cancel); const auto row=coordinates(mesh,atlas,mesh.triangles.row(i));
        const V3 a=row.coordinates.row(1)-row.coordinates.row(0),b=row.coordinates.row(2)-row.coordinates.row(0);
        if(a.cross(b).norm()<1e-15) continue;
        values[size_t(row.chart)].push_back(row.coordinates); result[size_t(row.chart)]->geometry.push_back(i);
    }
    for(size_t i=0;i<result.size();++i) { check_cancel(cancel); build(*result[i],values[i]); }
    return result;
}
static Location nearest(const ChartIndex& index,const V3& query) {
    if(index.geometry.empty()) return {};
    int id=-1; Eigen::RowVector3d point;
    const double distance=index.tree.squared_distance(index.vertices,index.triangles,query.transpose(),id,point);
    if(id<0||distance>1e-16) return {};
    const M3 coordinates=index.vertices.middleRows<3>(id*3);
    return {index.geometry[size_t(id)],barycentric(query,coordinates.row(0),coordinates.row(1),coordinates.row(2)),coordinates};
}
Location locate(const Indices& index,const Atlas& atlas,int chart,const V3& query,uint64_t cancel) {
    if(chart<0||chart>=int(index.size())) throw std::runtime_error("Material chart is no longer available.");
    const auto& c=atlas.charts[size_t(chart)];
    const int u=int(c.closed_v),v=int(c.closed_u);
    for(int i=-u;i<=u;++i) for(int j=-v;j<=v;++j) {
        check_cancel(cancel); const auto value=nearest(*index[size_t(chart)],query+V3(i,j,0));
        if(value.triangle>=0) return value;
    }
    return {};
}
}
