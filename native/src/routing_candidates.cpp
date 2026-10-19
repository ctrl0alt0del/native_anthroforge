#include "routing_planner.hpp"

namespace af::routing {
void unique_adjacent(Route& points) {
    points.erase(std::unique(points.begin(),points.end(),[](Vec a,Vec b) {
        return kernel::norm(kernel::sub(a,b))<=1e-10;
    }),points.end());
}
Route sampled(const Route& points,int count) {
    if(int(points.size())<=count) return points;
    Route output;
    for(int i=0;i<count;++i) output.push_back(points[size_t(std::nearbyint(double(i)*(points.size()-1)/(count-1)))]);
    return output;
}
static void face_shell(Route& points,const kernel::Bounds& bounds) {
    const Vec center=kernel::mul(kernel::add(kernel::load3(bounds.lo),kernel::load3(bounds.hi)),0.5);
    for(int axis=0;axis<3;++axis) for(int sign:{-1,1}) {
        Vec point=center; (&point.x)[axis]+=sign*(bounds.hi[axis]-bounds.lo[axis])*0.5;
        points.push_back(point);
    }
}
static void edge_shell(Route& points,const kernel::Bounds& bounds) {
    const Vec center=kernel::mul(kernel::add(kernel::load3(bounds.lo),kernel::load3(bounds.hi)),0.5);
    for(int axis=0;axis<3;++axis) {
        const int first=axis==0?1:0,last=axis==2?1:2;
        for(int a=0;a<2;++a) for(int b=0;b<2;++b) {
            Vec point=center; (&point.x)[first]=a?bounds.hi[first]:bounds.lo[first];
            (&point.x)[last]=b?bounds.hi[last]:bounds.lo[last]; points.push_back(point);
        }
    }
}
Route bounds_shell(const kernel::Bounds& source,double padding,bool dense) {
    auto bounds=source; Route points;
    for(int i=0;i<3;++i) { bounds.lo[i]-=padding; bounds.hi[i]+=padding; }
    for(int x=0;x<2;++x) for(int y=0;y<2;++y) for(int z=0;z<2;++z)
        points.push_back({x?bounds.hi[0]:bounds.lo[0],y?bounds.hi[1]:bounds.lo[1],z?bounds.hi[2]:bounds.lo[2]});
    face_shell(points,bounds); if(dense) edge_shell(points,bounds);
    return points;
}
static Route radial_shell(const kernel::AfInstance& item,double padding) {
    Route points; for(auto p:item.mesh->vertices) points.push_back(kernel::af_transform(item.matrix,p));
    points=sampled(points,32); Vec center{0,0,0};
    for(const auto& p:points) center=kernel::add(center,p);
    center=kernel::mul(center,1.0/points.size());
    for(auto& p:points) {
        const Vec delta=kernel::sub(p,center);
        p=kernel::add(p,kernel::mul(delta,padding/std::max(kernel::norm(delta),1e-12)));
    }
    return points;
}
static bool blocks(const Planning& plan,const kernel::AfInstance& item) {
    const auto row=kernel::af_instance_validation_row(item,plan.start,plan.end,plan.first,plan.last,plan.span,plan.threshold);
    return !row.clear;
}
static std::vector<const kernel::AfInstance*> active(const Planning& plan) {
    std::vector<const kernel::AfInstance*> rows,blocking;
    const auto bounds=kernel::af_segment_bounds(plan.start,plan.end,std::max(0.05,4*plan.input.options.radius));
    for(const auto& item:plan.world.collision->items) if(kernel::bounds_overlap(bounds,item.bounds)) {
        rows.push_back(&item); if(blocks(plan,item)) blocking.push_back(&item);
    }
    return blocking.empty()?rows:blocking;
}
Route compatibility(const Planning& plan) {
    Route rows{plan.start,plan.end}; const double pad=std::max(5*plan.input.options.radius,plan.world.floor);
    for(const auto* item:active(plan)) {
        check_cancel(plan.input.cancel); const auto radial=radial_shell(*item,4*pad),bounds=bounds_shell(item->bounds,pad,false);
        rows.insert(rows.end(),radial.begin(),radial.end()); rows.insert(rows.end(),bounds.begin(),bounds.end());
    }
    unique_adjacent(rows);
    if(rows.size()>96) { const auto rest=sampled(Route(rows.begin()+2,rows.end()),94);
        rows.resize(2); rows.insert(rows.end(),rest.begin(),rest.end()); }
    return rows;
}
Route resample(const Route& points,int count) {
    if(int(points.size())==count) return points;
    std::vector<double> lengths{0}; Route result;
    for(size_t i=1;i<points.size();++i) lengths.push_back(lengths.back()+kernel::norm(kernel::sub(points[i],points[i-1])));
    for(int i=0;i<count;++i) {
        const double target=lengths.back()*i/(count-1);
        const auto next=std::upper_bound(lengths.begin(),lengths.end(),target);
        const size_t index=std::min(size_t(std::max(ptrdiff_t(0),next-lengths.begin()-1)),points.size()-2);
        const double t=(target-lengths[index])/std::max(lengths[index+1]-lengths[index],1e-12);
        result.push_back(kernel::add(points[index],kernel::mul(kernel::sub(points[index+1],points[index]),t)));
    }
    return result;
}
}
