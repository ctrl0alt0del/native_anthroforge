#include "construction_internal.hpp"
int af_points_constrain_axes(const double* points,int count,const int* enabled,const double* values,double* output) {
    try {
        if(!points||!enabled||!values||!output||count<0||!af::V3(values).allFinite())
            throw std::runtime_error("Axis constraints require finite owned point inputs.");
        for(int i=0;i<count;++i) {
            const af::V3 value(points+3*i);
            if(!value.allFinite()) throw std::runtime_error("Invalid constrained point.");
            for(int axis=0;axis<3;++axis) output[3*i+axis]=enabled[axis]?values[axis]:value[axis];
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}

int af_points_transform(const double* points,int count,const double* matrix,double* output) {
    const af::M4 transform=Eigen::Map<const af::M4>(matrix);
    for(int i=0;i<count;++i) {
        Eigen::Map<af::V3> target(output+3*i);
        target=af::point(transform,af::V3(points+3*i));
    }
    return 0;
}
static std::vector<std::pair<double,int>> component_hits(const double* points,int count,const double* origin,const double* direction,double radius) {
    const af::V3 start(origin),ray=af::V3(direction).normalized();
    std::vector<std::pair<double,int>> hits;
    for(int i=0;i<count;++i) {
        const af::V3 delta=af::V3(points+3*i)-start;
        const double distance=delta.dot(ray);
        if(distance>=0&&(delta-distance*ray).squaredNorm()<=radius*radius)
            hits.emplace_back(distance,i);
    }
    std::sort(hits.begin(),hits.end());
    return hits;
}
int af_component_pick(const double* points,int count,const double* origin,const double* direction,double radius,int depth) {
    const auto hits=component_hits(points,count,origin,direction,radius);
    return hits.empty()?-1:hits[std::max(0,depth)%hits.size()].second;
}
int af_component_hits(const double* points,int count,const double* origin,const double* direction,double radius,double* output) {
    const auto hits=component_hits(points,count,origin,direction,radius);
    for(size_t i=0;i<hits.size();++i) { output[2*i]=hits[i].second; output[2*i+1]=hits[i].first; }
    return int(hits.size());
}
