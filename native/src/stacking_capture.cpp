// SPDX-License-Identifier: GPL-3.0-or-later
#include "stacking_internal.hpp"

namespace af::stacking {
static void exact(layer::Material& output,const AfStackMaterial& input) {
    pair::require(input.constraint_count>=0&&input.constraint_count<=2000000,"STACK_VECTOR_CONSTRAINT_SIZE");
    pair::require(!input.constraint_count||(input.constraints&&input.constraint_weights),"STACK_VECTOR_CONSTRAINT_INPUT");
    for(int i=0;i<input.constraint_count;++i) {
        afs::Row row{}; double sum=0; std::map<int,double> terms;
        for(int j=0;j<4;++j) {
            const auto id=input.constraints[4*i+j]; const double weight=input.constraint_weights[4*i+j];
            pair::require(id>=0&&id<output.mesh.vertices.rows()&&std::isfinite(weight),"STACK_VECTOR_CONSTRAINT_VALUE");
            terms[int(id)]+=weight; sum+=weight;
        }
        pair::require(std::abs(sum-1)<1e-9,"STACK_VECTOR_CONSTRAINT_SUM");
        for(const auto& term:terms) if(term.second!=0) row.terms.push_back(term);
        output.constraints.push_back(std::move(row));
    }
}
static layer::Material material(const AfStackDomain& input,const pair::Side& side) {
    const auto& m=input.material;
    const layer::ConstraintInput record{input.id,m.vertices,m.faces,m.interpolation,m.weights,m.fixed,
        m.vertices_count,m.faces_count,m.samples,m.width,m.fixed_count,1};
    auto output=layer::capture_material(record,side);
    exact(output,m); layer::normalize_material(output); return output;
}
void capture_domains(Inputs& input,const AfStackDomain* domains,int count,uint64_t cancel) {
    pair::require(count>=0&&count<=100000&&(!count||domains),"PAIR_INPUT_COUNT"); std::set<uint64_t> ids;
    for(int i=0;i<count;++i) {
        check_cancel(cancel); const auto& d=domains[i];
        pair::require(ids.insert(d.id).second,"PAIR_DUPLICATE_DOMAIN");
        pair::Input record{d.id,d.base,d.own,d.direction,d.faces,d.parts,d.sources,
            d.vertices,d.triangles,d.family,d.root,0,d.enabled,d.side,d.allowance};
        auto side=pair::capture(record);
        if(!layer::intrinsic_directions_valid(side)) input.state.invalid_directions.insert(d.id);
        try { input.state.materials.emplace(d.id,material(d,side)); }
        catch(const std::exception& e) { input.state.materials[d.id].error=e.what(); }
        input.work.incoming.push_back(std::move(side));
    }
}
void capture_obstacles(layer::State& state,const AfStackObstacle* inputs,int count,uint64_t cancel) {
    pair::require(count>=0&&count<=100000&&(!count||inputs),"STACK_OBSTACLES");
    for(int i=0;i<count;++i) {
        check_cancel(cancel); const auto& in=inputs[i]; pair::Side side;
        pair::require(in.vertices&&in.faces&&in.count>=3&&in.triangles>0,"STACK_OBSTACLE_INPUT");
        for(int j=0;j<in.count;++j) {
            const auto p=kernel::load3(in.vertices+3*j); pair::require(pair::finite(p),"STACK_OBSTACLE_COORDINATES"); side.base.push_back(p);
        }
        side.own=side.base; side.faces.assign(in.faces,in.faces+3*size_t(in.triangles));
        for(auto f:side.faces) pair::require(f>=0&&f<in.count,"STACK_OBSTACLE_INDEX");
        pair::prepare_snapshot(side,nullptr); const auto edges=layer::edge_counts(side);
        side.enabled=std::all_of(edges.begin(),edges.end(),[](const auto& edge){return edge.second==2;});
        state.obstacles.push_back(std::move(side));
    }
}
}
