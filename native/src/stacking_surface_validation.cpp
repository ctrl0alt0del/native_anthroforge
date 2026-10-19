// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_stacking.hpp"

namespace af::stacking {
using MaterialPoint=std::pair<tissue::stacking::Row,int64_t>;
struct CompleteSurface { pair::Side own,final; bool changed; };
static std::map<MaterialPoint,V3> material_positions(const Mesh& mesh,uint64_t cancel) {
    std::map<MaterialPoint,V3> output;
    for(int64_t i=0;i<mesh.vertices.rows();++i) {
        check_cancel(cancel); const auto row=tissue::stacking::row(mesh.tissue,size_t(i));
        const auto side=mesh.tissue.sides.at(size_t(i));
        output.emplace(MaterialPoint{row,side},mesh.vertices.row(i));
        if(side==0) for(int64_t value:{1,2}) output.emplace(MaterialPoint{row,value},mesh.vertices.row(i));
    }
    return output;
}
static V3 material_position(const std::map<MaterialPoint,V3>& positions,const Mesh& target,int64_t index) {
    const auto row=tissue::stacking::row(target.tissue,size_t(index)); const auto side=target.tissue.sides.at(size_t(index));
    auto found=positions.find({row,side});
    if(found==positions.end()&&target.tissue.kind==5&&(side==0||side==2)) found=positions.find({row,1});
    if(found==positions.end()) throw std::runtime_error("STACK_COMPLETE_MATERIAL_CORRESPONDENCE_MISSING");
    return found->second;
}
static pair::Side complete_own(const Mesh& own,const Mesh& final,const M4& frame,uint64_t cancel) {
    const auto positions=material_positions(own,cancel); pair::Side output;
    for(int64_t i=0;i<final.vertices.rows();++i) {
        check_cancel(cancel); const V3 value=point(frame,material_position(positions,final,i));
        output.base.push_back({value.x(),value.y(),value.z()});
    }
    output.own=output.base;
    for(int64_t i=0;i<final.triangles.rows();++i) for(int axis=0;axis<3;++axis) output.faces.push_back(final.triangles(i,axis));
    pair::prepare_snapshot(output,nullptr); return output;
}
static CompleteSurface complete_surface(const AfStackSurface& input,uint64_t cancel) {
    const auto own=mesh(input.intrinsic),final=mesh(input.final); const M4 frame=Eigen::Map<const M4>(input.frame);
    pair::require(frame.allFinite()&&std::abs(frame.determinant())>1e-18,"STACK_COMPLETE_FRAME");
    pair::require(own->tissue.kind>=3&&final->tissue.kind==own->tissue.kind,"STACK_COMPLETE_TISSUE_KIND");
    auto original=complete_own(*own,*final,frame,cancel); std::vector<kernel::Vec> points;
    for(int64_t i=0;i<final->vertices.rows();++i) {
        check_cancel(cancel); const V3 value=point(frame,final->vertices.row(i));
        points.push_back({value.x(),value.y(),value.z()});
    }
    auto next=layer::surface_copy(original,points);
    return {std::move(original),std::move(next),input.changed!=0};
}
static void validate_complete(const layer::State& state,const std::vector<CompleteSurface>& surfaces,std::atomic<bool>& cancel) {
    for(size_t i=0;i<surfaces.size();++i) {
        const auto& a=surfaces[i]; pair::require(!cancel,"PAIR_CANCELLED");
        if(a.changed) { layer::validate_final(a.own,a.final.own); layer::validate_collisions(a.own,a.final.own,state,cancel); }
        for(size_t j=0;j<i;++j) {
            const auto& b=surfaces[j]; if(!a.changed&&!b.changed) continue;
            layer::no_new_crossings(a.own,a.final,b.own,b.final,false,cancel);
        }
    }
}
}
int af_stack_validate_surfaces(uint64_t handle,const AfStackSurface* inputs,int count,uint64_t token) {
    try {
        if(!handle||count<0||count>100000||(!inputs&&count)) throw std::runtime_error("STACK_COMPLETE_INPUT");
        auto& engine=*reinterpret_cast<af::stacking::Engine*>(handle); std::lock_guard<std::mutex> lock(engine.mutex);
        std::atomic<bool> idle{false}; auto& cancel=token?reinterpret_cast<af::Cancellation*>(token)->cancelled:idle;
        std::vector<af::stacking::CompleteSurface> surfaces;
        for(int i=0;i<count;++i) if(af::mesh(inputs[i].final)->triangles.rows())
            surfaces.push_back(af::stacking::complete_surface(inputs[i],token));
        af::stacking::validate_complete(engine.state,surfaces,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
