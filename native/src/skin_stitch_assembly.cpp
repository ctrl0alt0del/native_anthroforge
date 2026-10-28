#include "skin_stitch.hpp"
namespace af::skin_stitch {
static double extent(const Quads& mesh) {
    Eigen::AlignedBox3d box; for(const auto& point:mesh.points) box.extend(point);
    return std::max(box.diagonal().norm(),1e-9);
}
static Vertices boundary_ring(const skin_annuli::Patch& patch) {
    const Vertices first=patch.points.topRows(patch.segments),last=patch.points.bottomRows(patch.segments);
    return skin_loops::perimeter(first)>=skin_loops::perimeter(last)?first:last;
}
static std::vector<Vertices> rings(const Quads& mesh,uint64_t cancel) {
    const auto loops=boundaries(mesh.faces,cancel); std::vector<Vertices> result;
    for(const auto& loop:loops) {
        Vertices ring(loop.size(),3); for(size_t i=0;i<loop.size();++i) ring.row(i)=mesh.points[loop[i]];
        result.push_back(std::move(ring));
    }
    return result;
}
static int match(const std::vector<Vertices>& loops,const Vertices& ring,const std::vector<bool>& used) {
    const V3 center=ring.colwise().mean(); int best=-1; double score=INFINITY;
    for(size_t i=0;i<loops.size();++i) if(!used[i]) {
        const double distance=(V3(loops[i].colwise().mean())-center).norm();
        if(distance<score) { best=int(i); score=distance; }
    }
    if(best<0) throw std::runtime_error("No available topology boundary for a LOOP annulus.");
    return best;
}
static std::vector<Transition> transitions(const Quads& mesh,const skin_annuli::Patches& patches,const Plane& plane,uint64_t cancel) {
    if(patches.empty()) return {};
    const auto loops=rings(mesh,cancel); std::vector<bool> used(loops.size(),false); std::vector<Transition> result;
    const double diagonal=extent(mesh);
    for(const auto& patch:patches) {
        check_cancel(cancel); const auto ring=boundary_ring(patch); const int index=match(loops,ring,used); used[index]=true;
        result.push_back(transition(loops[index],ring,plane,diagonal,cancel));
    }
    mirror_transitions(result,plane,diagonal,cancel); return result;
}
static Quads guide(const skin_annuli::Patch& patch,int index) {
    Quads result; result.faces=patch.faces;
    for(int i=0;i<patch.points.rows();++i) result.points.push_back(patch.points.row(i));
    result.regions.assign(result.faces.size(),skin_quads::Guide); result.guides.assign(result.faces.size(),index); return result;
}
static std::vector<Quads> parts(Quads source,const std::vector<Transition>& transitions,const skin_annuli::Patches& patches) {
    std::vector<Quads> result{std::move(source)};
    for(size_t i=0;i<transitions.size();++i) {
        auto mesh=transitions[i].mesh; mesh.guides.assign(mesh.faces.size(),int(i)); result.push_back(std::move(mesh));
    }
    for(size_t i=0;i<patches.size();++i) result.push_back(guide(patches[i],int(i)));
    return result;
}
Assembly assemble(Quads source,const skin_annuli::Patches& patches,const Plane& plane,bool allow_unstitched,uint64_t cancel) {
    Assembly result;
    try { result.transitions=transitions(source,patches,plane,cancel); }
    catch(const std::runtime_error& error) {
        check_cancel(cancel); if(!allow_unstitched) throw;
        result.warning=error.what();
    }
    const double tolerance=1e-6*extent(source);
    result.mesh=weld(parts(std::move(source),result.transitions,patches),tolerance,true,cancel);
    orient(result.mesh,cancel); return result;
}
}
