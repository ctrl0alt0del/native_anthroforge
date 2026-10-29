#include "anthroforge/inspection.h"
#include "stacking_internal.hpp"

namespace af::inspection {
using namespace stacking;
struct Scan { int limit,size=0; int64_t* ids; double* bounds; uint64_t cancel; };
static pair::Side snapshot(const Mesh& mesh,const M4& frame,uint64_t cancel) {
    pair::Side result;
    for(int64_t i=0;i<mesh.vertices.rows();++i) {
        check_cancel(cancel); const V3 p=point(frame,mesh.vertices.row(i)); result.base.push_back({p.x(),p.y(),p.z()});
    }
    result.own=result.base; result.faces.assign(mesh.triangles.data(),mesh.triangles.data()+mesh.triangles.size());
    pair::prepare_snapshot(result,nullptr); return result;
}
static void bounds(Eigen::AlignedBox3d& box,const pair::Side& side,int face) {
    for(int j=0;j<3;++j) { const auto p=side.base[size_t(side.faces[size_t(3*face+j)])]; box.extend(V3(p.x,p.y,p.z)); }
}
static void append(Scan& out,int kind,int other,const pair::Side& a,int first,const pair::Side& b,int second) {
    Eigen::AlignedBox3d box; bounds(box,a,first); if(second>=0) bounds(box,b,second);
    auto* ids=out.ids+4*out.size; ids[0]=kind; ids[1]=other; ids[2]=first; ids[3]=second;
    auto* values=out.bounds+6*out.size; std::copy(box.min().data(),box.min().data()+3,values);
    std::copy(box.max().data(),box.max().data()+3,values+3); ++out.size;
}
static bool straddles(const pair::Side& a,int first,const pair::Side& b,int second) {
    kernel::Vec p[3],q[3]; pair::face(a,first,p); pair::face(b,second,q);
    const V3 origin(p[0].x,p[0].y,p[0].z),u(p[1].x,p[1].y,p[1].z),v(p[2].x,p[2].y,p[2].z);
    const V3 n=(u-origin).cross(v-origin).normalized(); double lo=INFINITY,hi=-INFINITY,scale=1;
    for(const auto& point:q) { const V3 x(point.x,point.y,point.z); const double d=n.dot(x-origin);
        lo=std::min(lo,d); hi=std::max(hi,d); scale=std::max(scale,x.cwiseAbs().maxCoeff()); }
    const double tolerance=64*std::numeric_limits<double>::epsilon()*scale;
    return lo < -tolerance&&hi > tolerance;
}
struct Pair {
    const pair::Side &a,&b; int other;
    decltype(layer::edge_counts(std::declval<pair::Side>())) ea,eb;
};
static void candidates(Scan& out,const Pair& p,int face,int begin,int end) {
    for(int j=begin;j<end&&out.size<out.limit;++j) {
        check_cancel(out.cancel); const int other=p.b.snapshot->faces[size_t(j)].index;
        if(p.other<0&&(other<=face||layer::shared_vertex(p.a,face,other))) continue;
        if(straddles(p.a,face,p.b,other)&&straddles(p.b,other,p.a,face)&&layer::transverse(p.a,face,p.b,other,p.ea,p.eb))
            append(out,p.other<0?2:3,p.other,p.a,face,p.b,other);
    }
}
static void pairs(Scan& out,const pair::Side& a,const pair::Side& b,int other) {
    if(a.faces.empty()||b.faces.empty()) return;
    Pair pair{a,b,other,layer::edge_counts(a),layer::edge_counts(b)}; std::vector<int> stack;
    for(int face=0;face<int(a.faces.size()/3)&&out.size<out.limit;++face) {
        check_cancel(out.cancel); kernel::Vec p[3]; layer::face(a,face,p); const auto box=layer::triangle_box(p); stack={0};
        while(!stack.empty()&&out.size<out.limit) {
            check_cancel(out.cancel); const auto& node=b.snapshot->nodes[size_t(stack.back())]; stack.pop_back();
            if(!kernel::bounds_overlap(box,node.bounds)) continue;
            if(node.left>=0) { stack.push_back(node.left); stack.push_back(node.right); }
            else candidates(out,pair,face,node.begin,node.end);
        }
    }
}
static void degenerate(Scan& out,const pair::Side& a) {
    for(int f=0;f<int(a.faces.size()/3)&&out.size<out.limit;++f) {
        check_cancel(out.cancel); kernel::Vec p[3]; pair::face(a,f,p);
        const auto u=kernel::sub(p[1],p[0]),v=kernel::sub(p[2],p[0]); const double extent=std::max(kernel::norm(u),kernel::norm(v));
        if(kernel::norm(kernel::cross(u,v))<=extent*extent*1e-12) append(out,1,-1,a,f,a,-1);
    }
}
static void inspect(Scan& out,uint64_t target,const double* frame,const uint64_t* others,const double* frames,int count) {
    if(out.limit<1||out.limit>4096||count<0||count>65536||(count&&(!others||!frames)))
        throw std::runtime_error("Invalid bounded geometry check inputs.");
    const auto a=snapshot(*mesh(target),M4(frame),out.cancel); degenerate(out,a); pairs(out,a,a,-1);
    for(int i=0;i<count&&out.size<out.limit;++i) {
        check_cancel(out.cancel); const auto b=snapshot(*mesh(others[i]),M4(frames+16*i),out.cancel); pairs(out,a,b,i);
    }
}
}
int af_inspection_findings(uint64_t target,const double* frame,const uint64_t* others,const double* frames,
    int count,int limit,int64_t* ids,double* bounds,int64_t* total,uint64_t cancel) {
    try {
        if(!frame||!ids||!bounds||!total) throw std::runtime_error("Missing geometry check buffers.");
        af::inspection::Scan scan{limit,0,ids,bounds,cancel};
        af::inspection::inspect(scan,target,frame,others,frames,count); *total=scan.size; return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_inspection_face_lines(uint64_t handle,const double* frame,int triangle,double* lines) {
    try {
        const auto mesh=af::mesh(handle); const af::M4 matrix(frame);
        if(triangle<0||triangle>=mesh->triangles.rows()) throw std::runtime_error("Unknown finding triangle.");
        for(int j=0;j<6;++j) {
            const auto id=mesh->triangles(triangle,(j/2+j%2)%3); const af::V3 p=af::point(matrix,mesh->vertices.row(id));
            std::copy(p.data(),p.data()+3,lines+3*j);
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_inspection_faces_lines(uint64_t handle,const double* frame,const int64_t* triangles,int count,double* lines) {
    try {
        const auto mesh=af::mesh(handle);
        if(!frame||count<0||count>mesh->triangles.rows()||(count&&(!triangles||!lines)))
            throw std::runtime_error("Invalid region outline buffers.");
        for(int i=0;i<count;++i) {
            if(triangles[i]<0||triangles[i]>=mesh->triangles.rows())
                throw std::runtime_error("Unknown region triangle.");
            if(af_inspection_face_lines(handle,frame,static_cast<int>(triangles[i]),lines+18*i)) return 1;
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
