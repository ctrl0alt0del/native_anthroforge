// SPDX-License-Identifier: GPL-3.0-or-later
// Side evaluation retains each receiving tissue's settings and publishes as one group.
namespace af::stacking {
struct Group {
    std::map<uint64_t,Engine*> owners;
    std::map<Engine*,std::set<uint64_t>> targets;
    std::map<uint64_t,layer::Solved> output;
    layer::Graph graph;
    std::set<uint64_t> selected,accepted;
};
static Group group_targets(const AfStackTarget* rows,int count) {
    pair::require(count>0&&count<=100000&&rows,"STACK_GROUP_INPUT"); Group group;
    for(int i=0;i<count;++i) {
        pair::require(rows[i].session&&group.selected.insert(rows[i].id).second,"STACK_GROUP_TARGET");
        auto* owner=reinterpret_cast<Engine*>(rows[i].session);
        group.owners[rows[i].id]=owner; group.targets[owner].insert(rows[i].id);
    }
    return group;
}
static void group_plan(Group& group) {
    for(const auto& entry:group.targets) {
        auto& engine=*entry.first; layer::own_outputs(engine.state,engine.session);
        const auto graph=layer::plan(engine.state);
        for(auto id:entry.second) {
            pair::require(graph.parents.count(id),"STACK_GROUP_UNKNOWN_TARGET");
            group.graph.parents[id]=graph.parents.at(id);
            for(auto parent:graph.parents.at(id)) { group.graph.parents[parent]; group.graph.children[parent].insert(id); }
            if(graph.blocked.count(id)) { group.graph.blocked.insert(id); group.graph.reasons[id]=graph.reasons.at(id); }
        }
    }
}
static void group_accepted(Group& group,const AfStackAccepted* rows,int count) {
    pair::require(count>=0&&count<=100000&&(!count||rows),"STACK_GROUP_ACCEPTED");
    for(const auto& entry:group.targets) {
        auto& engine=*entry.first;
        auto accepted=accepted_inputs(engine.state,group.graph,rows,count,group.selected);
        group.accepted.insert(accepted.begin(),accepted.end());
        for(auto id:entry.second) group.output[id]=engine.state.outputs.at(id);
        for(auto id:accepted) group.output[id]=engine.state.outputs.at(id);
    }
}
static void install_group_outputs(Group& group,Engine& engine) {
    for(const auto& row:group.output) {
        pair::require(engine.state.outputs.count(row.first),"STACK_GROUP_SCENE_MISMATCH");
        engine.state.outputs[row.first]=row.second;
    }
}
static void group_solve(Group& group,std::atomic<bool>& cancel) {
    auto pending=group.selected,done=group.accepted; cycles(group.graph,cancel);
    while(!pending.empty()) {
        pair::require(!cancel,"PAIR_CANCELLED"); const auto next=ready(group.graph,pending,done);
        if(next.empty()) break;
        for(auto id:next) {
            auto& engine=*group.owners.at(id); install_group_outputs(group,engine);
            layer::evaluate_layer(engine.state,engine.session,group.graph,{id},cancel);
            group.output[id]=engine.state.outputs.at(id); pending.erase(id); done.insert(id);
        }
    }
}
static void group_validate(Group& group,std::atomic<bool>& cancel) {
    for(const auto& entry:group.targets) {
        auto& engine=*entry.first; install_group_outputs(group,engine);
        std::set<uint64_t> accepted=group.accepted;
        for(auto id:group.selected) if(!entry.second.count(id)) accepted.insert(id);
        neighbors(engine.state,engine.session,group.graph,entry.second,accepted,cancel);
    }
    for(const auto& entry:group.targets) {
        auto& engine=*entry.first; failures(engine.state,group.graph);
        reset_failed(engine.state,engine.session,group.graph,entry.second);
        layer::evict_solved(engine.state,engine.session);
    }
    pair::require(!cancel,"PAIR_CANCELLED");
}
static void resolve_group(Group& group,const AfStackAccepted* rows,int count,std::atomic<bool>& cancel) {
    std::vector<std::unique_lock<std::mutex>> locks;
    std::map<Engine*,std::map<uint64_t,layer::Solved>> previous;
    for(const auto& entry:group.targets) locks.emplace_back(entry.first->mutex);
    for(const auto& entry:group.targets) previous[entry.first]=entry.first->state.outputs;
    try {
        group_plan(group); group_accepted(group,rows,count); group_solve(group,cancel); group_validate(group,cancel);
    } catch(...) {
        for(auto& entry:previous) entry.first->state.outputs=std::move(entry.second);
        throw;
    }
}
}
int af_stack_resolve_group(const AfStackTarget* targets,int target_count,const AfStackAccepted* accepted,int count,uint64_t token) {
    try {
        auto group=af::stacking::group_targets(targets,target_count);
        std::atomic<bool> idle{false}; auto& cancel=token?reinterpret_cast<af::Cancellation*>(token)->cancelled:idle;
        af::stacking::resolve_group(group,accepted,count,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
