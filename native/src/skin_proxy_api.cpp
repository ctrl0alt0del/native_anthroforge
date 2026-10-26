#include "skin_decimate.hpp"
#include "anthroforge/skin_density.h"
namespace af::skin_decimate {
static Work capture(const Mesh& mesh,uint64_t cancel) {
    Work input{mesh.vertices.cast<float>().cast<double>(),mesh.triangles};
    if(!input.vertices.allFinite()) throw std::runtime_error("Skin proxy coordinates exceed float range.");
    for(int i=0;i<input.faces.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        const auto ids=input.faces.row(i);
        if(ids[0]==ids[1]||ids[0]==ids[2]||ids[1]==ids[2]) throw std::runtime_error("Skin proxy contains repeated triangle indices.");
        const auto n=normal(input.vertices,ids);
        if(!n.allFinite()||n.isZero()) throw std::runtime_error("Skin proxy contains a degenerate triangle.");
    }
    return input;
}
static std::shared_ptr<Mesh> result(const Work& work,uint64_t cancel) {
    Points points; Faces faces; points.reserve(work.vertices.rows()); faces.reserve(work.faces.rows());
    for(int i=0;i<work.vertices.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        points.push_back(work.vertices.row(i));
    }
    for(int i=0;i<work.faces.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        faces.push_back({work.faces(i,0),work.faces(i,1),work.faces(i,2)});
    }
    return make_mesh(points,faces,cancel);
}
std::shared_ptr<Mesh> evaluate(const Mesh& mesh,int target,uint64_t budget,uint64_t cancel) {
    State state; state.cancel=cancel; state.budget=budget;
    state.storage=uint64_t(mesh.triangles.rows())*2048+uint64_t(mesh.vertices.rows())*512;
    if(state.storage>budget) throw std::runtime_error("Skin proxy preparation exceeds worker memory budget.");
    const auto input=capture(mesh,cancel); prepare(state,input);
    return result(reduce(input,state,target),cancel);
}
}
uint64_t af_skin_proxy_decimate(uint64_t handle,int target,uint64_t budget,uint64_t cancel) {
    try {
        if(target<1||!budget) throw std::runtime_error("Invalid skin proxy face target or memory budget.");
        af::check_cancel(cancel); const auto mesh=af::mesh(handle);
        if(target>=mesh->triangles.rows()) return af::retain(mesh);
        target=std::max(target,int(mesh->triangles.rows()/100));
        return af::retain(af::skin_decimate::evaluate(*mesh,target,budget,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
