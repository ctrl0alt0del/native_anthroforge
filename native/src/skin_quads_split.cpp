#include "skin_quads.hpp"
#include <numeric>
namespace af::skin_quads {
std::array<Edge,4> edges(const Quad& face) {
    std::array<Edge,4> result;
    for(int i=0;i<4;++i) result[i]=std::minmax(face[i],face[(i+1)%4]);
    return result;
}
static std::array<int,4> flags(const Quad& face,const std::set<Edge>& split) {
    const auto values=edges(face); std::array<int,4> result{};
    for(int i=0;i<4;++i) result[i]=split.count(values[i])!=0;
    return result;
}
static bool close_once(const Quads& source,std::set<Edge>& split,uint64_t cancel) {
    bool changed=false;
    for(size_t i=0;i<source.faces.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        const auto row=flags(source.faces[i],split); const int count=std::accumulate(row.begin(),row.end(),0);
        const auto keys=edges(source.faces[i]);
        if(count==1) { const int offset=int(std::find(row.begin(),row.end(),1)-row.begin()); split.insert(keys[(offset+2)%4]); changed=true; }
        if(count==3) { const int offset=int(std::find(row.begin(),row.end(),0)-row.begin()); split.insert(keys[offset]); changed=true; }
    }
    return changed;
}
static std::set<Edge> closed_edges(const Quads& source,const Mask& selected,uint64_t cancel) {
    std::set<Edge> split;
    for(size_t i=0;i<source.faces.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        if(selected[i]) { const auto values=edges(source.faces[i]); split.insert(values.begin(),values.end()); }
    }
    while(close_once(source,split,cancel)) check_cancel(cancel);
    return split;
}
static std::map<Edge,int64_t> midpoints(Quads& output,const std::set<Edge>& split,uint64_t cancel) {
    std::map<Edge,int64_t> result;
    for(const auto& edge:split) {
        if(result.size()%4096==0) check_cancel(cancel);
        result[edge]=int64_t(output.points.size());
        output.points.push_back((output.points[edge.first]+output.points[edge.second])*.5);
    }
    return result;
}
static std::vector<Quad> opposite(const Quad& f,const Quad& m,int k) {
    return {{f[k],m[k],m[(k+2)%4],f[(k+3)%4]}, {m[k],f[(k+1)%4],f[(k+2)%4],m[(k+2)%4]}};
}
static std::vector<Quad> centered(const Quad& f,const Quad& m,int64_t center,int count) {
    std::vector<Quad> result;
    if(count==4) {
        for(int i=0;i<4;++i) result.push_back({f[i],m[i],center,m[(i+3)%4]});
        return result;
    }
    int k=0; while(k<4&&(m[k]<0||m[(k+1)%4]<0)) ++k;
    if(k==4) throw std::runtime_error("Incomplete conforming quad split.");
    return {{f[k],m[k],center,f[(k+3)%4]}, {m[k],f[(k+1)%4],m[(k+1)%4],center},
            {center,m[(k+1)%4],f[(k+2)%4],f[(k+3)%4]}};
}
static std::vector<Quad> split_face(const Quad& f,const std::map<Edge,int64_t>& mid,Points& points) {
    const auto keys=edges(f); Quad m{-1,-1,-1,-1}; int count=0;
    for(int j=0;j<4;++j) { const auto found=mid.find(keys[j]); if(found!=mid.end()) { m[j]=found->second; ++count; } }
    if(count==0) return {f};
    if(count==2&&m[0]>=0&&m[2]>=0) return opposite(f,m,0);
    if(count==2&&m[1]>=0&&m[3]>=0) return opposite(f,m,1);
    const auto center=int64_t(points.size()); V3 p=V3::Zero(); for(auto i:f) p+=points[i];
    points.push_back(p*.25); return centered(f,m,center,count);
}
Quads split(const Quads& source,const Mask& selected,uint64_t cancel) {
    if(selected.size()!=source.faces.size()) throw std::runtime_error("Quad refinement selection does not match polygons.");
    if(source.faces.size()>1000000) throw std::runtime_error("Quad refinement exceeds the geometry budget.");
    const auto closed=closed_edges(source,selected,cancel); Quads result; result.points=source.points;
    const auto mid=midpoints(result,closed,cancel);
    for(size_t i=0;i<source.faces.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        const auto faces=split_face(source.faces[i],mid,result.points);
        result.faces.insert(result.faces.end(),faces.begin(),faces.end());
        result.regions.insert(result.regions.end(),faces.size(),source.regions[i]);
        result.guides.insert(result.guides.end(),faces.size(),source.guides[i]);
    }
    return result;
}
}
