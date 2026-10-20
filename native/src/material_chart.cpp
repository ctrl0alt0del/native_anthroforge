// SPDX-License-Identifier: GPL-3.0-or-later
#include "material_chart.hpp"

namespace af::material {
static void append(Atlas& atlas,Chart chart,uint64_t cancel) {
    const auto id=int(atlas.charts.size());
    for(const auto& [vertex,position]:chart.points) {
        check_cancel(cancel); atlas.membership.at(size_t(vertex)).push_back(id);
    }
    atlas.charts.push_back(std::move(chart));
}
static Chart grid_chart(const MaterialGrid& grid,uint64_t cancel) {
    Chart chart; chart.closed_u=grid.closed_u; chart.closed_v=grid.closed_v;
    for(int i=0;i<grid.rows;++i) for(int j=0;j<grid.columns;++j) {
        check_cancel(cancel);
        chart.points.emplace(grid.indices[size_t(i*grid.columns+j)],V3(grid.across[size_t(i)],grid.along[size_t(j)],0));
    }
    return chart;
}
static Chart patch_chart(const MaterialBasis& basis,uint64_t cancel) {
    Chart chart;
    for(int64_t i=0;i<basis.count;++i) {
        check_cancel(cancel); const V3 value(basis.parameters.data()+3*i);
        chart.points.emplace(i,V3(value.x(),value.y(),0));
        if(value.z()!=-1&&(value.z()<0||value.z()>=1)) throw std::runtime_error("Invalid patch perimeter parameter.");
        if(value.z()>=0&&!chart.boundary.emplace(value.z(),value.head<2>()).second)
            throw std::runtime_error("Duplicate patch perimeter parameter.");
    }
    if(chart.boundary.size()<3) throw std::runtime_error("Material patch has no closed boundary.");
    return chart;
}
Atlas atlas(const MaterialBasis& basis,uint64_t cancel) {
    validate_basis(basis); Atlas result; result.membership.resize(size_t(basis.count));
    if(basis.grids.empty()) append(result,patch_chart(basis,cancel),cancel);
    else {
        Mesh view; view.vertices.resize(basis.count,3); view.material=basis.grids; view.material_axes=basis.parameters;
        for(const auto& grid:material_grids(view)) append(result,grid_chart(grid,cancel),cancel);
    }
    return result;
}
static binding::Weights weights(const Mesh& mesh,int vertex) {
    if(vertex<0||vertex>=mesh.vertices.rows()) throw std::runtime_error("Invalid retained material triangle.");
    return mesh.tissue.kind>=3?binding::weights(mesh.tissue,vertex):binding::Weights{{vertex,1}};
}
static V3 unwrapped(V3 value,const V3& origin,const Chart& chart) {
    if(chart.closed_v) value[0]-=std::round(value[0]-origin[0]);
    if(chart.closed_u) value[1]-=std::round(value[1]-origin[1]);
    return value;
}
static bool belongs(const Chart& chart,const std::array<binding::Weights,3>& rows) {
    for(const auto& row:rows) for(const auto& [index,weight]:row)
        if(weight>1e-14&&chart.points.find(index)==chart.points.end()) return false;
    return true;
}
static V3 interpolate(const Chart& chart,const binding::Weights& row,const V3& origin) {
    V3 result=V3::Zero();
    for(const auto& [index,weight]:row) if(weight>1e-14) result+=weight*unwrapped(chart.points.at(index),origin,chart);
    return result;
}
static void sides(Triangle& result,const Mesh& mesh,const Eigen::Vector3i& vertices) {
    if(mesh.tissue.kind<3) return;
    int64_t fallback=1;
    for(int vertex:vertices) fallback=std::max(fallback,mesh.tissue.sides[size_t(vertex)]);
    for(int i=0;i<3;++i) {
        const auto side=mesh.tissue.sides[size_t(vertices[i])];
        result.coordinates(i,2)=(side?side:fallback)==2?-1:1;
    }
}
Triangle coordinates(const Mesh& mesh,const Atlas& atlas,const Eigen::Vector3i& vertices) {
    const std::array<binding::Weights,3> rows{weights(mesh,vertices[0]),weights(mesh,vertices[1]),weights(mesh,vertices[2])};
    const auto first=rows[0].begin()->first;
    for(int id:atlas.membership.at(size_t(first))) {
        const auto& chart=atlas.charts[size_t(id)]; if(!belongs(chart,rows)) continue;
        Triangle result; result.chart=id; const auto origin=chart.points.at(first);
        for(int i=0;i<3;++i) result.coordinates.row(i)=interpolate(chart,rows[size_t(i)],origin);
        sides(result,mesh,vertices); return result;
    }
    throw std::runtime_error("Surface triangle crosses unrelated material charts; explicitly rebind.");
}
}
