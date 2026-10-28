#include "skin_stitch.hpp"
namespace af::skin_stitch {
static std::vector<int64_t> reflection_map(const Vertices& points) {
    const auto tree=skin_loops::point_index(points,0); std::vector<int64_t> result;
    for(int i=0;i<points.rows();++i) {
        V3 p=points.row(i); p.x()*=-1; const auto hit=tree->nearest(points,p);
        if(hit.second>1e-8) throw std::runtime_error("Skin transition vertices are not symmetric across the requested plane.");
        result.push_back(hit.first);
    }
    return result;
}
static std::vector<int64_t> cyclic(int count,int start,int end,int step) {
    std::vector<int64_t> result{start}; int current=start;
    while(current!=end) { current=(current+step+count)%count; result.push_back(current); }
    return result;
}
static double average_x(const Vertices& points,const std::vector<int64_t>& indices) {
    double sum=0; for(const auto i:indices) sum+=points(i,0); return sum/indices.size();
}
static std::vector<int64_t> negative_half(const Vertices& points) {
    const auto map=reflection_map(points); int top=-1,bottom=-1;
    for(int i=0;i<points.rows();++i) if(map[i]==i) {
        if(top<0||points(i,2)>points(top,2)) top=i;
        if(bottom<0||points(i,2)<points(bottom,2)) bottom=i;
    }
    if(top<0||bottom<0||top==bottom) throw std::runtime_error("Centered skin transition needs two distinct points on its plane.");
    auto forward=cyclic(int(points.rows()),top,bottom,1),backward=cyclic(int(points.rows()),top,bottom,-1);
    return average_x(points,forward)<average_x(points,backward)?forward:backward;
}
static std::vector<Quad> reflected_quads(std::vector<Quad> source,const std::vector<int64_t>& mapping) {
    const auto count=source.size();
    for(size_t i=0;i<count;++i) {
        Quad reflected; for(int j=0;j<4;++j) reflected[j]=mapping[source[i][3-j]]; source.push_back(reflected);
    }
    return source;
}
static std::vector<Quad> odd_quads(const std::vector<Triangle>& triangles,const std::vector<int64_t>& mapping,bool start) {
    const Triangle center=start?triangles.front():triangles.back(); Triangle opposite;
    for(int i=0;i<3;++i) opposite[i]=mapping[center[i]];
    const std::vector<Triangle> rest(start?triangles.begin()+1:triangles.begin(),start?triangles.end():triangles.end()-1);
    auto result=reflected_quads(paired(rest),mapping); result.insert(result.begin(),join(center,opposite)); return result;
}
static Vertices selected(const Vertices& points,const std::vector<int64_t>& indices) {
    Vertices result(indices.size(),3);
    for(size_t i=0;i<indices.size();++i) result.row(i)=points.row(indices[i]); return result;
}
std::vector<Quad> centered_faces(const Vertices& first,const Vertices& second) {
    Vertices all(first.rows()+second.rows(),3); all<<first,second;
    auto a=negative_half(first),b=negative_half(second);
    const auto steps=moves(selected(first,a),selected(second,b),false); for(auto& i:b) i+=first.rows();
    const auto triangles=zipper(a,b,steps,false); const auto mapping=reflection_map(all);
    if(triangles.size()%2==0) { auto result=reflected_quads(paired(triangles),mapping); validate(result,int(first.rows()),int(second.rows())); return result; }
    auto result=odd_quads(triangles,mapping,true);
    try { validate(result,int(first.rows()),int(second.rows())); return result; }
    catch(const std::runtime_error&) { result=odd_quads(triangles,mapping,false); }
    validate(result,int(first.rows()),int(second.rows())); return result;
}
}
