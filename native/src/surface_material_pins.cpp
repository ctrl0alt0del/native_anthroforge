// SPDX-License-Identifier: GPL-3.0-or-later
// Preserve authored structural locations when a surface accepts its construction inputs.
#include "material_pins.hpp"
#include "surface_branch_internal.hpp"

namespace af {
namespace cs=curve_surface;
struct PinPosition { double length=-1; };
struct PinLayout {
    cs::Rows rows;
    std::vector<cs::Branch> branches;
    std::vector<MaterialGrid> grids;
    std::vector<double> stations;
    std::unique_ptr<Surface> patch;
};
static double directed(double first,double second,const cs::Row& row) {
    const double delta=(second-first)*row.direction;
    return delta<0?delta+row.extent:delta;
}
static PinPosition position(const cs::Row& row,int parameter) {
    const auto stations=cs::stations(row); const auto count=row.points.size();
    if(parameter<0||parameter>=row.extent) throw std::runtime_error("Structural pin requires an authored point parameter.");
    for(size_t a=0;a+1<count+size_t(row.closed);++a) {
        const auto b=(a+1)%count; const double width=directed(row.parameters[a],row.parameters[b],row);
        const double d=directed(row.parameters[a],parameter,row);
        if(d>width+1e-12||width<=1e-14) continue;
        const double t=std::clamp(d/width,0.,1.);
        return {(1-t)*stations[a]+t*stations[a+1]};
    }
    return {};
}
static PinLayout layout(const Mesh& mesh,const AfSurfacePins& inputs,uint64_t cancel) {
    PinLayout result; result.rows=cs::inputs(inputs.rows,inputs.count,true,cancel);
    result.grids=material_grids(mesh);
    if(inputs.branch_count) result.branches=cs::branch_inputs(result.rows,inputs.main_count,inputs.branches,inputs.branch_count);
    else if(!result.grids.empty()&&inputs.exact) {
        for(const auto& row:result.rows) {
            auto values=cs::stations(row); if(row.closed) values.pop_back();
            result.stations.insert(result.stations.end(),values.begin(),values.end());
        }
        result.stations=cs::unique_stations(std::move(result.stations));
    }
    if(result.grids.empty()) result.patch=std::make_unique<Surface>(mesh,M4::Identity());
    return result;
}
static double column(const std::vector<double>& stations,double factor,bool closed) {
    const auto end=std::upper_bound(stations.begin(),stations.end(),factor);
    const size_t a=size_t(std::max(std::ptrdiff_t(0),end-stations.begin()-1)),b=a+1;
    const double last=b<stations.size()?stations[b]:1;
    const double t=last>stations[a]?(factor-stations[a])/(last-stations[a]):0;
    return (double(a)+t)/double(stations.size()-size_t(!closed));
}
static std::array<double,11> grid_pin(const PinLayout& layout,const AfSurfacePins& inputs,int row,PinPosition position) {
    std::array<double,11> pin{}; pin[2]=position.length;
    if(inputs.branch_count) {
        if(row<inputs.main_count) { pin[1]=double(row)/(inputs.main_count-1); return pin; }
        for(size_t i=0;i<layout.branches.size();++i) {
            const auto& b=layout.branches[i]; const auto found=std::find(b.rows.begin(),b.rows.end(),row);
            if(found!=b.rows.end()) { pin[0]=double(i+1); pin[1]=(b.roots[size_t(found-b.rows.begin())]-b.roots.front())/(b.roots.back()-b.roots.front()); return pin; }
        }
        throw std::runtime_error("Structural source is missing from accepted branch layout.");
    }
    if(!inputs.across) throw std::runtime_error("Structural loft pins need accepted row density.");
    int index=0; for(int i=0;i<row;++i) index+=inputs.across[i]+1;
    pin[1]=double(index)/(layout.grids[0].rows-int(!layout.grids[0].closed_v));
    pin[2]=inputs.exact?column(layout.stations,position.length,layout.rows[0].closed):position.length;
    return pin;
}
static std::array<double,11> patch_pin(const PinLayout& layout,int row,PinPosition position) {
    const auto& source=layout.rows[size_t(row)]; const auto point=cs::sample(source,cs::stations(source),position.length);
    const auto hit=nearest(*layout.patch,point);
    if(hit.triangle<0||(hit.point-point).norm()>1e-8) throw std::runtime_error("Structural patch pin has no retained boundary correspondence.");
    std::array<double,11> result{}; result[0]=-1;
    for(int i=0;i<3;++i) { result[size_t(3+i)]=(*layout.patch->triangles)(hit.triangle,i); result[size_t(7+i)]=hit.weights[i]; }
    return result;
}
std::vector<double> material_capture(const Mesh& mesh,const AfSurfacePins& inputs,uint64_t cancel) {
    if(inputs.point_count<0||inputs.point_count>262144||(inputs.point_count&&!inputs.points)) throw std::runtime_error("Invalid structural point count.");
    const auto prepared=layout(mesh,inputs,cancel); std::vector<double> result;
    for(int i=0;i<inputs.point_count;++i) {
        check_cancel(cancel); const int row=inputs.points[2*i],point=inputs.points[2*i+1];
        if(row<0||row>=inputs.count) throw std::runtime_error("Structural pin references an absent curve.");
        const auto p=position(prepared.rows[size_t(row)],point); if(p.length<0) continue;
        const auto value=prepared.patch?patch_pin(prepared,row,p):grid_pin(prepared,inputs,row,p);
        result.insert(result.end(),value.begin(),value.end());
    }
    return result;
}
}
