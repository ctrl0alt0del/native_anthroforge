// SPDX-License-Identifier: GPL-3.0-or-later
namespace af::stacking {
static void accepted_points(layer::Solved& output,const AfStackAccepted& input) {
    pair::require(input.count==int(output.points.size())&&(!input.count||input.points),"STACK_ACCEPTED_TOPOLOGY_MISMATCH");
    output.summary.maximum=0;
    for(int i=0;i<input.count;++i) {
        const auto value=kernel::load3(input.points+3*i); pair::require(pair::finite(value),"STACK_ACCEPTED_NONFINITE");
        output.summary.maximum=std::max(output.summary.maximum,kernel::norm(kernel::sub(value,output.points[size_t(i)])));
        output.points[size_t(i)]=value;
    }
    output.summary.status=input.status;
}
static std::set<uint64_t> accepted_inputs(layer::State& state,layer::Graph& graph,const AfStackAccepted* rows,int count,const std::set<uint64_t>& targets) {
    std::set<uint64_t> accepted;
    for(int i=0;i<count;++i) {
        const auto& row=rows[i]; pair::require(!targets.count(row.id)&&state.outputs.count(row.id)&&accepted.insert(row.id).second,"STACK_ACCEPTED_ID");
        pair::require(row.status>=0&&row.status<=3,"STACK_ACCEPTED_STATUS");
        if(row.status>1) { graph.blocked.insert(row.id); graph.reasons[row.id]="STACK_FAILED_ACCEPTED_PREREQUISITE"; }
        else accepted_points(state.outputs.at(row.id),row);
    }
    for(auto id:targets) for(auto parent:graph.parents.at(id)) if(!targets.count(parent)&&!accepted.count(parent)) {
        graph.blocked.insert(id); graph.reasons[id]="STACK_ACCEPTED_PREREQUISITE_UNAVAILABLE:"+std::to_string(parent);
    }
    layer::propagate(graph); return accepted;
}
static void solve_targets(layer::State& state,const pair::Session& detection,layer::Graph& graph,const std::set<uint64_t>& targets,std::atomic<bool>& cancel) {
    std::set<uint64_t> pending=targets,done;
    for(const auto& item:state.outputs) if(!targets.count(item.first)) done.insert(item.first);
    while(!pending.empty()) {
        pair::require(!cancel,"PAIR_CANCELLED"); const auto next=ready(graph,pending,done);
        if(next.empty()) {
            for(auto id:pending) { graph.blocked.insert(id); graph.reasons[id]="STACK_DEPENDENCY_CYCLE_OR_DESCENDANT"; }
            break;
        }
        layer::evaluate_layer(state,detection,graph,next,cancel);
        for(auto id:next) { pending.erase(id); done.insert(id); }
    }
}
static void contact(layer::State& state,layer::Graph& graph,const layer::SurfacePair& a,const layer::SurfacePair& b,const std::set<uint64_t>& targets,std::atomic<bool>& cancel) {
    if(!pair::eligible(a.final,b.final)||!pair::intersects(a.sweep,b.sweep)) return;
    if(state.outputs.at(a.final.id).summary.maximum==0&&state.outputs.at(b.final.id).summary.maximum==0) return;
    try { layer::validate_neighbor(a,b,state,cancel); }
    catch(const std::exception& error) {
        if(cancel) throw;
        for(auto id:{a.final.id,b.final.id}) if(targets.count(id)) {
            graph.blocked.insert(id); graph.reasons[id]=error.what();
        }
    }
}
static void neighbors(layer::State& state,const pair::Session& detection,layer::Graph& graph,const std::set<uint64_t>& targets,const std::set<uint64_t>& accepted,std::atomic<bool>& cancel) {
    const auto surfaces=layer::final_snapshots(state,detection);
    for(auto first=surfaces.begin();first!=surfaces.end();++first) for(auto second=std::next(first);second!=surfaces.end();++second) {
        pair::require(!cancel,"PAIR_CANCELLED"); const auto a=first->first,b=second->first;
        if(!targets.count(a)&&!targets.count(b)) continue;
        if(graph.blocked.count(a)||graph.blocked.count(b)) continue;
        if((!targets.count(a)&&!accepted.count(a))||(!targets.count(b)&&!accepted.count(b))) continue;
        contact(state,graph,first->second,second->second,targets,cancel);
    }
    layer::propagate(graph);
}
static void reset_failed(layer::State& state,const pair::Session& detection,const layer::Graph& graph,const std::set<uint64_t>& targets) {
    for(auto id:targets) if(graph.blocked.count(id)) {
        auto& output=state.outputs.at(id); output.points=detection.sides[detection.indices.at(id)].own;
        output.bonus.resize(0); output.summary.maximum=0;
    }
}
static void resolve_outputs(Engine& engine,const AfStackAccepted* rows,int count,const uint64_t* targets,int target_count,std::atomic<bool>& cancel) {
    pair::require(count>=0&&count<=100000&&(!count||rows)&&target_count>0&&target_count<=100000&&targets,"STACK_ACCEPTED_INPUT");
    std::set<uint64_t> selected(targets,targets+target_count); pair::require(selected.size()==size_t(target_count),"STACK_DUPLICATE_TARGET");
    auto& state=engine.state; layer::own_outputs(state,engine.session); auto graph=layer::plan(state); cycles(graph,cancel);
    for(auto id:selected) pair::require(state.outputs.count(id),"STACK_UNKNOWN_TARGET");
    const auto accepted=accepted_inputs(state,graph,rows,count,selected);
    solve_targets(state,engine.session,graph,selected,cancel); neighbors(state,engine.session,graph,selected,accepted,cancel);
    failures(state,graph); reset_failed(state,engine.session,graph,selected); layer::evict_solved(state,engine.session);
    pair::require(!cancel,"PAIR_CANCELLED");
}
void resolve(Engine& engine,const AfStackAccepted* rows,int count,const uint64_t* targets,int target_count,std::atomic<bool>& cancel) {
    auto previous=engine.state.outputs;
    try { resolve_outputs(engine,rows,count,targets,target_count,cancel); }
    catch(...) { engine.state.outputs=std::move(previous); throw; }
}
}
int af_stack_resolve(uint64_t handle,const AfStackAccepted* accepted,int count,const uint64_t* targets,int target_count,uint64_t cancel) {
    try {
        if(!handle) throw std::runtime_error("Missing stacking session.");
        auto& engine=*reinterpret_cast<af::stacking::Engine*>(handle); std::lock_guard<std::mutex> lock(engine.mutex);
        std::atomic<bool> idle{false}; auto& cancelled=cancel?reinterpret_cast<af::Cancellation*>(cancel)->cancelled:idle;
        af::stacking::resolve(engine,accepted,count,targets,target_count,cancelled); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
