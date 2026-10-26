#include "skin_density.hpp"
#include "anthroforge/skin_density.h"
namespace af::skin_density {
static void initial_values(const double* initial,int64_t count,double* output) {
    for(int64_t i=0;i<count;++i) {
        if(!std::isfinite(initial[i])||initial[i]<0) throw std::runtime_error("Invalid initial density lengths.");
        output[i]=initial[i];
    }
}
}
int af_skin_density_base_count(uint64_t handle,const double* lengths,int requested,int reserved,uint64_t cancel) {
    try {
        if(!lengths||requested<1||requested>500000||reserved<0) throw std::runtime_error("Invalid topology base budget.");
        const auto mesh=af::mesh(handle); std::vector<double> areas(mesh->vertices.rows());
        af::skin_density::areas(*mesh,areas.data(),cancel); double total=0,maximum=0;
        for(size_t i=0;i<areas.size();++i) {
            if(i%4096==0) af::check_cancel(cancel);
            if(!std::isfinite(lengths[i])||lengths[i]<0) throw std::runtime_error("Invalid density length.");
            total+=areas[i]; maximum=std::max(maximum,lengths[i]);
        }
        const double count=std::nearbyint(total/std::max(maximum*maximum,1e-20))+reserved;
        return int(std::min(double(requested),std::max(1000.,count)));
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
namespace af::skin_density {
static void report(const std::vector<Region>& regions,double* areas,int* unusable) {
    for(size_t i=0;i<regions.size();++i) {
        const auto& region=regions[i]; areas[i]=region.area;
        unusable[i]=region.vertices.empty()||region.area<=0||region.budget<=0;
    }
}
}
int af_skin_density(uint64_t handle,const int* ids,const double* budgets,int count,const double* initial,
                    int iterations,double* lengths,double* areas,double* region_areas,int* unusable,uint64_t cancel) {
    try {
        if(count<1||count>1000000||iterations<0||iterations>100||!ids||!budgets||!lengths||!areas||!region_areas||!unusable)
            throw std::runtime_error("Invalid topology density buffers or settings.");
        af::check_cancel(cancel); const auto mesh=af::mesh(handle); af::skin_density::areas(*mesh,areas,cancel);
        const auto regions=af::skin_density::regions(*mesh,ids,budgets,count,areas,cancel);
        if(initial) af::skin_density::initial_values(initial,mesh->vertices.rows(),lengths);
        else af::skin_density::initialize(regions,mesh->vertices.rows(),lengths);
        af::skin_density::smooth(*mesh,regions,areas,lengths,iterations,cancel);
        af::skin_density::report(regions,region_areas,unusable); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
