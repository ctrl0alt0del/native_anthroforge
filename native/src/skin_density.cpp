#include "skin_density.hpp"
namespace af::skin_density {
void areas(const Mesh& mesh,double* result,uint64_t cancel) {
    std::fill(result,result+mesh.vertices.rows(),0.); std::vector<double> thirds(mesh.triangles.rows());
    for(int i=0;i<mesh.triangles.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        const V3 a=mesh.vertices.row(mesh.triangles(i,0)),b=mesh.vertices.row(mesh.triangles(i,1));
        const V3 c=mesh.vertices.row(mesh.triangles(i,2)); thirds[i]=(b-a).cross(c-a).norm()/6.;
    }
    for(int j=0;j<3;++j) for(int i=0;i<mesh.triangles.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        result[mesh.triangles(i,j)]+=thirds[i];
    }
}
std::vector<Region> regions(const Mesh& mesh,const int* ids,const double* budgets,int count,const double* areas,uint64_t cancel) {
    std::vector<Region> result(count);
    for(int i=0;i<count;++i) {
        if(!std::isfinite(budgets[i])||budgets[i]<0) throw std::runtime_error("Invalid exclusive quad budget.");
        result[i].budget=budgets[i];
    }
    for(int i=0;i<mesh.vertices.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        if(ids[i]<0||ids[i]>=count) throw std::runtime_error("Invalid topology density region.");
        auto& region=result[ids[i]]; region.vertices.push_back(i); region.area+=areas[i];
    }
    return result;
}
static double median(std::vector<double> values) {
    if(values.empty()) return 1.;
    std::sort(values.begin(),values.end()); const size_t n=values.size();
    return n%2?values[n/2]:(values[n/2-1]+values[n/2])*.5;
}
void initialize(const std::vector<Region>& regions,int64_t count,double* lengths) {
    std::fill(lengths,lengths+count,0.); std::vector<double> positive;
    for(const auto& region:regions) {
        if(region.vertices.empty()||region.area<=0||region.budget<=0) continue;
        const double edge=std::sqrt(region.area/region.budget);
        for(int index:region.vertices) { lengths[index]=edge; positive.push_back(edge); }
    }
    const double fallback=median(std::move(positive));
    for(int64_t i=0;i<count;++i) if(lengths[i]<=0) lengths[i]=fallback;
}
static Neighbors adjacency(const Mesh& mesh,uint64_t cancel) {
    Neighbors result(mesh.vertices.rows());
    for(int i=0;i<mesh.triangles.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        for(int j=0;j<3;++j) {
            const int a=mesh.triangles(i,j),b=mesh.triangles(i,(j+1)%3);
            result[a].insert(b); result[b].insert(a);
        }
    }
    return result;
}
static void step(const Neighbors& neighbors,double* values,uint64_t cancel) {
    std::vector<double> logs(neighbors.size());
    for(size_t i=0;i<logs.size();++i) logs[i]=std::log(std::max(values[i],1e-12));
    for(size_t i=0;i<logs.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        if(neighbors[i].empty()) continue;
        double total=0; for(int linked:neighbors[i]) total+=logs[linked];
        values[i]=std::exp(.65*logs[i]+.35*total/double(neighbors[i].size()));
    }
}
static void correct(const std::vector<Region>& regions,const double* areas,double* values,uint64_t cancel) {
    for(const auto& region:regions) {
        check_cancel(cancel); if(region.vertices.empty()||region.budget<=0) continue;
        double predicted=0;
        for(int i:region.vertices) predicted+=areas[i]/std::max(values[i]*values[i],1e-20);
        const double scale=std::sqrt(predicted/region.budget);
        for(int i:region.vertices) values[i]*=scale;
    }
}
void smooth(const Mesh& mesh,const std::vector<Region>& regions,const double* areas,double* values,int iterations,uint64_t cancel) {
    if(!iterations) return;
    const auto neighbors=adjacency(mesh,cancel);
    for(int i=0;i<iterations;++i) { check_cancel(cancel); step(neighbors,values,cancel); correct(regions,areas,values,cancel); }
}
}
