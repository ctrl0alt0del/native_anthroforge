#include "skin_centerlines.hpp"
#include <climits>

namespace af::skin {
static void leaf(const Centerlines& lines,int edge,const V3& p,LineHit& hit) {
    const V3 a=lines.index.vertices.row(lines.index.edges(edge,0));
    const V3 b=lines.index.vertices.row(lines.index.edges(edge,1)),d=b-a;
    const double t=d.squaredNorm()>1e-30?std::clamp((p-a).dot(d)/d.squaredNorm(),0.,1.):0;
    const V3 q=a+t*d; const double distance=(p-q).norm();
    if(distance<hit.distance) hit={q,distance,t,edge,lines.owners[edge],lines.locals[edge]};
}
static void query(const Centerlines& lines,const ComponentTree& tree,const V3& p,
                  const std::vector<int>& excluded,LineHit& hit) {
    if(tree.m_box.squaredExteriorDistance(p)>hit.distance*hit.distance) return;
    const int edge=tree.m_primitive;
    if(edge>=0) {
        if(std::find(excluded.begin(),excluded.end(),lines.owners[edge])==excluded.end()) leaf(lines,edge,p,hit);
    } else {
        if(tree.m_left) query(lines,*tree.m_left,p,excluded,hit);
        if(tree.m_right) query(lines,*tree.m_right,p,excluded,hit);
    }
}
LineHit Centerlines::nearest(const V3& point,double reach,const std::vector<int>& excluded) const {
    LineHit result; result.distance=reach;
    if(!owners.empty()) query(*this,index.tree,point,excluded,result);
    return result;
}
static void endpoint(Centerlines& lines,const double* xyz,int vertices,int64_t vertex,int position) {
    if(vertex<0||vertex>=vertices) throw std::runtime_error("Invalid skin segment index.");
    const V3 value(xyz+3*vertex);
    if(!value.allFinite()) throw std::runtime_error("Nonfinite skin centerline position.");
    lines.index.vertices.row(position)=value;
}
static void elements(Centerlines& lines,const double* xyz,int vertices,const int64_t* edges,
                     const int* owners,int count,int sources,uint64_t cancel) {
    std::vector<int> totals(sources); lines.index.edges.resize(count,2);
    lines.index.vertices.resize(2LL*count,3);
    for(int i=0;i<count;++i) {
        if(i%4096==0) check_cancel(cancel);
        if(owners[i]<0||owners[i]>=sources) throw std::runtime_error("Invalid skin centerline owner.");
        lines.owners.push_back(owners[i]); lines.locals.push_back(totals[owners[i]]++);
        for(int j=0;j<2;++j) {
            endpoint(lines,xyz,vertices,edges[2LL*i+j],2*i+j);
            lines.index.edges(i,j)=2*i+j;
        }
    }
}
std::shared_ptr<Centerlines> centerlines(const double* xyz,int vertices,const int64_t* edges,
    const int* owners,int count,int sources,uint64_t cancel) {
    if(!xyz||vertices<2||count<0||count>INT_MAX/2||sources<1||(count&&(!edges||!owners)))
        throw std::runtime_error("Missing skin centerline buffers.");
    if(!count) { check_cancel(cancel); return nullptr; }
    auto result=std::make_shared<Centerlines>();
    elements(*result,xyz,vertices,edges,owners,count,sources,cancel);
    if(count) result->index.tree.init(result->index.vertices,result->index.edges);
    check_cancel(cancel); return result;
}
}
