// Experimental non-iterative propagation; never linked into the application.
#include <Eigen/Dense>
#include <algorithm>
#include <vector>
#include <cmath>
#include <stdexcept>
#include <string>
#define API extern "C" __declspec(dllexport)
using V=Eigen::Vector3d;
using M=Eigen::Matrix3d;
using Points=std::vector<V>;
struct Region { std::vector<int> ids; V center; M inverse; double ridge; };
struct Map { M linear; V translation; V apply(const V& p) const { return linear*p+translation; } };
struct Trial { int samples,rows,parents,regions; double width; Points points; std::vector<double> arc,weights; std::vector<int> counts,pins,pin_parents; std::vector<std::vector<Region>> patches; std::vector<Points> bones; };
static thread_local std::string last_error;
static double kernel(double x) {
    x=std::abs(x); if(x>=1) return 0;
    return std::pow(1-x,4)*(1+4*x);
}
static Points read(const double* data,int count) {
    Points points; points.reserve(count);
    for(int i=0;i<count;++i) points.emplace_back(data+3*i);
    return points;
}
static V mean(const Points& points,const std::vector<int>& ids) {
    V result=V::Zero(); for(int i:ids) result+=points[size_t(i)];
    return result/double(ids.size());
}
static Region patch(const Points& vertices,const V& center,int neighbors) {
    std::vector<std::pair<double,int>> order;
    for(size_t i=0;i<vertices.size();++i) order.emplace_back((vertices[i]-center).squaredNorm(),int(i));
    const size_t count=std::min(size_t(neighbors),order.size());
    std::partial_sort(order.begin(),order.begin()+count,order.end());
    Region region; for(size_t i=0;i<count;++i) region.ids.push_back(order[i].second);
    region.center=mean(vertices,region.ids); M covariance=M::Zero();
    for(int i:region.ids) { V p=vertices[size_t(i)]-region.center; covariance+=p*p.transpose(); }
    region.ridge=std::max(covariance.trace()*1e-4,1e-12);
    region.inverse=(covariance+region.ridge*M::Identity()).inverse(); return region;
}
static V curve_point(const Trial& t,double s) {
    auto it=std::lower_bound(t.arc.begin(),t.arc.begin()+t.samples,s);
    int high=std::clamp(int(it-t.arc.begin()),1,t.samples-1),low=high-1;
    const double f=(s-t.arc[size_t(low)])/(t.arc[size_t(high)]-t.arc[size_t(low)]);
    return t.points[size_t(low)]*(1-f)+t.points[size_t(high)]*f;
}
static void prepare_regions(Trial& t,const double* raw,int neighbors) {
    int offset=0;
    for(int count:t.counts) {
        const auto points=read(raw+3*offset,count); offset+=count;
        std::vector<Region> regions;
        for(int j=0;j<t.regions;++j) regions.push_back(patch(points,curve_point(t,t.arc[size_t(t.samples-1)]*j/(t.regions-1)),neighbors));
        t.patches.push_back(std::move(regions)); t.bones.push_back(points);
    }
}
static double cell(const Trial& t,int j) {
    if(j==0) return (t.arc[1]-t.arc[0])*.5;
    if(j==t.samples-1) return (t.arc[size_t(j)]-t.arc[size_t(j-1)])*.5;
    return (t.arc[size_t(j+1)]-t.arc[size_t(j-1)])*.5;
}
static double smoothed(const Trial& t,const double* original,int row,int parent) {
    double sum=0,total=0;
    for(int j=0;j<t.samples;++j) {
        const double w=kernel((t.arc[size_t(row)]-t.arc[size_t(j)])/t.width)*cell(t,j);
        sum+=w*original[j*t.parents+parent]; total+=w;
    }
    return sum/std::max(total,1e-20);
}
static double pin_width(const Trial& t,int p) {
    double available=t.arc[size_t(t.samples-1)]; const int node=t.pins[size_t(p)];
    if(p) available=std::min(available,t.arc[size_t(node)]-t.arc[size_t(t.pins[size_t(p-1)])]);
    if(p+1<int(t.pins.size())) available=std::min(available,t.arc[size_t(t.pins[size_t(p+1)])]-t.arc[size_t(node)]);
    return std::min(t.width,.45*available);
}
static void constrain_weights(Trial& t,int row) {
    for(size_t p=0;p<t.pins.size();++p) {
        const double w=kernel((t.arc[size_t(row)]-t.arc[size_t(t.pins[p])])/pin_width(t,int(p)));
        for(int b=0;b<t.parents;++b) t.weights[size_t(row*t.parents+b)]*=1-w;
        t.weights[size_t(row*t.parents+t.pin_parents[p])]+=w;
    }
}
static void prepare_weights(Trial& t,const double* original) {
    t.weights.resize(size_t(t.rows*t.parents));
    for(int i=0;i<t.rows;++i) {
        for(int b=0;b<t.parents;++b) t.weights[size_t(i*t.parents+b)]=smoothed(t,original,i,b);
        constrain_weights(t,i);
    }
}
API const char* trial_error() { return last_error.c_str(); }
API void* trial_prepare(int n,int rows,int parents,const double* points,const double* arc,const double* weights,const int* counts,const double* vertices,int pins,const int* indices,const int* owners,int regions,int neighbors,double width) {
    try {
        if(n<3||rows<n||parents<1||regions<2||neighbors<4||width<=0) throw std::runtime_error("Invalid experimental buffers.");
        auto* t=new Trial{n,rows,parents,regions,width};
        t->points=read(points,rows); t->arc.assign(arc,arc+rows);
        t->counts.assign(counts,counts+parents); t->pins.assign(indices,indices+pins); t->pin_parents.assign(owners,owners+pins);
        prepare_regions(*t,vertices,neighbors); prepare_weights(*t,weights); return t;
    } catch(const std::exception& e) { last_error=e.what(); return nullptr; }
}
static Map fit(const Region& patch,const Points& before,const double* after) {
    V center=V::Zero(); for(int i:patch.ids) center+=V(after+3*i); center/=double(patch.ids.size()); M cross=M::Zero();
    for(int i:patch.ids) cross+=(V(after+3*i)-center)*(before[size_t(i)]-patch.center).transpose();
    Eigen::JacobiSVD<M> svd(cross,Eigen::ComputeFullU|Eigen::ComputeFullV);
    M sign=M::Identity(); sign(2,2)=(svd.matrixU()*svd.matrixV().transpose()).determinant()<0?-1:1;
    const M rotation=svd.matrixU()*sign*svd.matrixV().transpose();
    const M linear=(cross+patch.ridge*rotation)*patch.inverse;
    return {linear,center-linear*patch.center};
}
static std::vector<std::vector<Map>> maps(const Trial& t,const double* before,const double* after) {
    std::vector<std::vector<Map>> result; int offset=0;
    for(int b=0;b<t.parents;++b) {
        const double* c=after+3*offset; offset+=t.counts[size_t(b)]; std::vector<Map> own;
        for(const auto& patch:t.patches[size_t(b)]) own.push_back(fit(patch,t.bones[size_t(b)],c));
        result.push_back(std::move(own));
    }
    return result;
}
static V regional(const Trial& t,const std::vector<Map>& maps,int row) {
    const double u=t.arc[size_t(row)]/t.arc[size_t(t.samples-1)]*(t.regions-1);
    const int low=std::clamp(int(u),0,t.regions-2); const double f=u-low;
    const double weights[4]{std::pow(1-f,3)/6,(3*f*f*f-6*f*f+4)/6,(-3*f*f*f+3*f*f+3*f+1)/6,f*f*f/6};
    V result=V::Zero();
    for(int j=0;j<4;++j) result+=weights[j]*maps[size_t(std::clamp(low+j-1,0,t.regions-1))].apply(t.points[size_t(row)]);
    return result;
}
static Points blended(const Trial& t,const std::vector<std::vector<Map>>& maps) {
    Points result(size_t(t.rows),V::Zero());
    for(int i=0;i<t.rows;++i) for(int b=0;b<t.parents;++b)
        result[size_t(i)]+=t.weights[size_t(i*t.parents+b)]*regional(t,maps[size_t(b)],i);
    return result;
}
static void exact_pins(const Trial& t,Points& points,const double* goals) {
    Points delta;
    for(size_t p=0;p<t.pins.size();++p) delta.push_back(V(goals+3*p)-points[size_t(t.pins[p])]);
    for(int i=0;i<t.rows;++i) for(size_t p=0;p<t.pins.size();++p)
        points[size_t(i)]+=kernel((t.arc[size_t(i)]-t.arc[size_t(t.pins[p])])/pin_width(t,int(p)))*delta[p];
}
API int trial_evaluate(void* handle,const double* before,const double* after,const double* goals,double* output) {
    try {
        const auto& t=*static_cast<Trial*>(handle); const auto transforms=maps(t,before,after);
        auto points=blended(t,transforms); exact_pins(t,points,goals);
        for(int i=0;i<t.rows;++i) { if(!points[size_t(i)].allFinite()) throw std::runtime_error("Nonfinite experimental output."); Eigen::Map<V>(output+3*i)=points[size_t(i)]; }
        return 0;
    } catch(const std::exception& e) { last_error=e.what(); return 1; }
}
API void trial_weights(void* handle,double* output) {
    const auto& t=*static_cast<Trial*>(handle); std::copy(t.weights.begin(),t.weights.end(),output);
}
API void trial_release(void* handle) { delete static_cast<Trial*>(handle); }

API void trial_arcs(int samples,int rows,const double* points,const int* nodes,double* arc) {
    arc[0]=0;
    for(int i=1;i<samples;++i) arc[i]=arc[i-1]+(V(points+3*i)-V(points+3*(i-1))).norm();
    for(int i=samples;i<rows;++i) arc[i]=arc[nodes[i]];
}
API void trial_parameters(int count,const double* parameters,int knots,const double* stations,double* output) {
    for(int i=0;i<count;++i) {
        const double s=parameters[i]; const double* upper=std::upper_bound(stations,stations+knots,s);
        const int j=std::clamp(int(upper-stations)-1,0,knots-2);
        output[i]=j+(s-stations[j])/(stations[j+1]-stations[j]);
    }
}
