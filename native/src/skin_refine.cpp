#include "skin_quads.hpp"
namespace af::skin_quads {
static std::vector<double> sample_lengths(const Quads& current,const Mesh& density,const double* lengths,uint64_t cancel) {
    std::vector<int> ids(density.vertices.rows()); for(size_t i=0;i<ids.size();++i) ids[i]=int(i);
    if(ids.empty()) throw std::runtime_error("Refinement needs density vertices.");
    const skin_ownership::PointIndex tree(density.vertices,ids,cancel); std::vector<double> values(current.points.size());
    for(size_t i=0;i<values.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        values[i]=lengths[tree.nearest(density.vertices,current.points[i]).first];
    }
    return values;
}
static std::vector<double> scores(const Quads& current,const std::vector<double>& lengths,uint64_t cancel) {
    std::vector<double> result(current.faces.size());
    for(size_t i=0;i<result.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        const auto f=current.faces[i]; const V3 a=current.points[f[0]],b=current.points[f[1]],c=current.points[f[2]],d=current.points[f[3]];
        const double area=.5*((b-a).cross(c-a).norm()+(c-a).cross(d-a).norm());
        double edge=0; for(auto v:f) edge+=lengths[v]*.25;
        result[i]=area/std::max(edge*edge,1e-20);
    }
    return result;
}
static Quads best_refinement(const Quads& source,const std::vector<std::vector<int>>& ordered,int target,uint64_t cancel) {
    int low=1,high=int(ordered.size()); Quads best=source;
    for(int iteration=0;iteration<8&&low<=high;++iteration) {
        check_cancel(cancel); const int count=(low+high)/2; Mask mask(source.faces.size(),0);
        for(int i=0;i<count;++i) for(int v:ordered[i]) mask[v]=1;
        auto trial=split(source,mask,cancel); const int size=int(trial.faces.size());
        if(even_boundaries(trial,cancel)&&std::abs(size-target)<std::abs(int(best.faces.size())-target)) best=std::move(trial);
        if(size<target) low=count+1; else high=count-1;
    }
    return best;
}
Quads refine(Quads source,const Mesh& density,const double* lengths,int target,int passes,const double* plane,uint64_t cancel) {
    for(int i=0;i<density.vertices.rows();++i) if(!std::isfinite(lengths[i])||lengths[i]<0) throw std::runtime_error("Invalid refinement density.");
    for(int pass=0;pass<passes;++pass) {
        check_cancel(cancel); if(int(source.faces.size())>=target) break;
        const auto lengths_at_vertices=sample_lengths(source,density,lengths,cancel);
        const auto ordered=candidates(source,scores(source,lengths_at_vertices,cancel),plane,cancel);
        if(ordered.empty()) break;
        auto result=best_refinement(source,ordered,target,cancel);
        if(result.faces.size()==source.faces.size()) break;
        source=std::move(result);
    }
    return source;
}
}
uint64_t af_skin_refine(uint64_t handle,uint64_t density,const double* lengths,const int* regions,const int* guides,
                       int target,int passes,const double* plane,uint64_t cancel) {
    try {
        if(!lengths||target<1||target>500000||passes<0||passes>2) throw std::runtime_error("Invalid adaptive skin refinement settings.");
        auto source=af::skin_quads::capture(*af::mesh(handle),regions,guides,cancel);
        auto result=af::skin_quads::refine(std::move(source),*af::mesh(density),lengths,target,passes,plane,cancel);
        return af::skin_quads::retain(af::skin_quads::complete(std::move(result),cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
