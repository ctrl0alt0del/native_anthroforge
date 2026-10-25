#include "fiber_deformation.hpp"
#include <Eigen/LU>
#include <map>
namespace af::fiber {
static V3 anchor(const Mesh& mesh,const double* r) {
    V3 p=V3::Zero();
    for(int i=0;i<3;++i) {
        if(r[i]<0||r[i]>=mesh.vertices.rows()||std::floor(r[i])!=r[i]) throw std::runtime_error("Invalid retained fiber triangle.");
        p+=r[3+i]*mesh.vertices.row(int(r[i])).transpose();
    }
    return p;
}
static M3 capture_basis(const double* r) {
    const V3 x=V3(r+21).normalized(),z=V3(r+24).normalized(); M3 b;
    b.col(0)=x; b.col(1)=z.cross(x).normalized(); b.col(2)=x.cross(b.col(1)); return b;
}
static M3 reference_basis(const Mesh& mesh,const double* r) {
    const V3 a=mesh.vertices.row(int(r[0])),b=mesh.vertices.row(int(r[1])),c=mesh.vertices.row(int(r[2]));
    const V3 x=(b-a).normalized(),z=(b-a).cross(c-a).normalized(); M3 basis;
    basis.col(0)=x; basis.col(1)=z.cross(x).normalized(); basis.col(2)=z; return basis;
}
struct Evidence { std::vector<V3> local,world; M3 rotation=M3::Identity(); };
static Evidence evidence(const Preparation& v,const AfFiberReference& in,int parent) {
    Evidence e; const auto mesh=af::mesh(in.meshes[parent]);
    for(int i=0;i<v.points.rows();++i) for(int j=0;j<2;++j) {
        if(in.owners[2*i+j]!=parent||in.weights[2*i+j]<=0) continue;
        const double* r=in.bindings+28*(2*i+j); const V3 p=anchor(*mesh,r); const M3 basis=capture_basis(r);
        e.local.push_back(p); e.world.push_back(v.points.row(i).transpose()-basis*V3(r+15));
        if(e.local.size()==1) e.rotation=basis*reference_basis(*mesh,r).transpose();
    }
    if(e.local.empty()) throw std::runtime_error("Unused fiber reference surface.");
    return e;
}
M4 recovered_frame(const Preparation& v,const AfFiberReference& in,int parent) {
    const auto e=evidence(v,in,parent); V3 a=V3::Zero(),b=V3::Zero();
    for(size_t i=0;i<e.local.size();++i) { a+=e.local[i]; b+=e.world[i]; }
    a/=double(e.local.size()); b/=double(e.local.size()); M3 covariance=M3::Zero(),cross=M3::Zero();
    for(size_t i=0;i<e.local.size();++i) { covariance+=(e.local[i]-a)*(e.local[i]-a).transpose(); cross+=(e.world[i]-b)*(e.local[i]-a).transpose(); }
    const double ridge=std::max(covariance.trace()*1e-12,1e-16);
    const M3 linear=(cross+ridge*e.rotation)*(covariance+ridge*M3::Identity()).inverse();
    M4 result=M4::Identity(); result.block<3,3>(0,0)=linear; result.block<3,1>(0,3)=b-linear*a;
    for(size_t i=0;i<e.local.size();++i) if((point(result,e.local[i])-e.world[i]).norm()>1e-6*std::max(1.0,v.length))
        throw std::runtime_error("Older fiber capture cannot recover its bind frame; use Local Surface Following or explicitly rebind.");
    return result;
}
static Region region(const Vertices& vertices,const V3& center) {
    std::vector<std::pair<double,int>> nearest;
    for(int i=0;i<vertices.rows();++i) nearest.emplace_back((vertices.row(i).transpose()-center).squaredNorm(),i);
    const size_t count=std::min(size_t(64),nearest.size());
    std::partial_sort(nearest.begin(),nearest.begin()+count,nearest.end()); Region r; r.center=V3::Zero();
    for(size_t i=0;i<count;++i) { r.ids.push_back(nearest[i].second); r.center+=vertices.row(nearest[i].second); }
    r.center/=double(count); M3 covariance=M3::Zero();
    for(int i:r.ids) { const V3 p=vertices.row(i).transpose()-r.center; covariance+=p*p.transpose(); }
    r.ridge=std::max(covariance.trace()*1e-4,1e-12);
    r.inverse=(covariance+r.ridge*M3::Identity()).inverse(); return r;
}
static void vertex_records(Parent& p,const std::map<int,int>& lookup) {
    p.records.assign(p.indices.size()*28,0); std::vector<bool> found(p.indices.size(),false);
    for(int face=0;face<p.mesh->triangles.rows();++face) for(int slot=0;slot<3;++slot) {
        const auto entry=lookup.find(p.mesh->triangles(face,slot));
        if(entry==lookup.end()||found[size_t(entry->second)]) continue;
        double* r=p.records.data()+28*entry->second;
        for(int j=0;j<3;++j) r[j]=p.mesh->triangles(face,j);
        r[3+slot]=1; r[12]=r[21]=r[26]=1; found[size_t(entry->second)]=true;
    }
    if(std::find(found.begin(),found.end(),false)!=found.end()) throw std::runtime_error("Smooth fiber support contains loose vertices.");
}
static void compact(Parent& p) {
    std::map<int,int> lookup;
    for(auto& r:p.regions) for(auto& index:r.ids) {
        const int id=index; const auto entry=lookup.emplace(id,int(lookup.size()));
        if(entry.second) p.indices.push_back(id);
        index=entry.first->second;
    }
    Vertices selected(p.indices.size(),3);
    for(size_t i=0;i<p.indices.size();++i) selected.row(int(i))=p.vertices.row(p.indices[i]);
    p.vertices=std::move(selected); vertex_records(p,lookup);
}
void prepare_parents(Preparation& v,const AfFiberReference& in,uint64_t cancel) {
    for(int b=0;b<in.surfaces;++b) {
        check_cancel(cancel); Parent p; p.reference=in.meshes[b]; p.mesh=mesh(p.reference);
        if(in.groups[b]<0||in.groups[b]>b) throw std::runtime_error("Invalid fiber support group.");
        if(in.groups[b]!=b) { p.alias=in.groups[b]; v.parents.push_back(std::move(p)); continue; }
        p.frame=Eigen::Map<const M4>(in.frames+16*b);
        if(p.frame.isZero()) p.frame=recovered_frame(v,in,b);
        if(!p.frame.allFinite()||!p.frame.fullPivLu().isInvertible()||p.mesh->vertices.rows()<1)
            throw std::runtime_error("Invalid fiber support reference frame.");
        p.vertices.resize(p.mesh->vertices.rows(),3);
        for(int i=0;i<p.vertices.rows();++i) p.vertices.row(i)=point(p.frame,p.mesh->vertices.row(i));
        for(int j=0;j<8;++j) p.regions.push_back(region(p.vertices,curve_point(v,v.length*j/(v.path->closed?8:7))));
        compact(p); v.parents.push_back(std::move(p));
    }
}
}
