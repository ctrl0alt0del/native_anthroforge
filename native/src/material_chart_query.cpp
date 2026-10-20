// SPDX-License-Identifier: GPL-3.0-or-later
#include "material_chart.hpp"

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
static void candidates(const igl::AABB<Vertices,3>& tree,const V3& query,std::vector<int>& ids,uint64_t cancel) {
    check_cancel(cancel);
    if(tree.m_box.squaredExteriorDistance(query)>1e-16) return;
    if(tree.is_leaf()) { if(tree.m_primitive>=0) ids.push_back(tree.m_primitive); return; }
    if(tree.m_left) candidates(*tree.m_left,query,ids,cancel);
    if(tree.m_right) candidates(*tree.m_right,query,ids,cancel);
}
static Location candidate(const ChartIndex& index,const V3& query,int id) {
    const M3 coordinates=index.vertices.middleRows<3>(id*3);
    const V3 weights=barycentric(query,coordinates.row(0),coordinates.row(1),coordinates.row(2));
    if(weights.minCoeff()<-1e-8||(coordinates.transpose()*weights-query).squaredNorm()>1e-16) return {};
    return {index.geometry[size_t(id)],weights,coordinates};
}
static Location nearest(const ChartIndex& index,const V3& query,const Tangents& directions,uint64_t cancel) {
    if(index.geometry.empty()) return {};
    std::vector<int> ids; candidates(index.tree,query,ids,cancel);
    const V3 normal=directions.col(0).cross(directions.col(1)).normalized();
    Location result; double best=-1;
    for(int id:ids) {
        const auto found=candidate(index,query,id); if(found.triangle<0) continue;
        const V3 a=found.coordinates.row(1)-found.coordinates.row(0),b=found.coordinates.row(2)-found.coordinates.row(0);
        const double alignment=std::abs(normal.dot(a.cross(b).normalized()));
        if(alignment>best) { result=found; best=alignment; }
    }
    return result;
}
Location locate(const Indices& index,const Atlas& atlas,int chart,const V3& query,const Tangents& directions,uint64_t cancel) {
    if(chart<0||chart>=int(index.size())) throw std::runtime_error("Material chart is no longer available.");
    const auto& c=atlas.charts[size_t(chart)];
    const int u=int(c.closed_v),v=int(c.closed_u);
    for(int i=-u;i<=u;++i) for(int j=-v;j<=v;++j) {
        check_cancel(cancel); const auto value=nearest(*index[size_t(chart)],query+V3(i,j,0),directions,cancel);
        if(value.triangle>=0) return value;
    }
    return {};
}
}
