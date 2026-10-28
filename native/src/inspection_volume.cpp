#include "anthroforge/inspection.h"
#include "mesh_internal.hpp"
#include "../boolean/qualification.hpp"

namespace af::inspection {
static Vertices world_vertices(const Mesh& mesh,const M4& frame,uint64_t cancel) {
    Vertices values(mesh.vertices.rows(),3);
    for(int i=0;i<values.rows();++i) { check_cancel(cancel); values.row(i)=point(frame,mesh.vertices.row(i)); }
    if(!values.allFinite()) throw std::runtime_error("Volume inspection needs finite coordinates.");
    return values;
}
static Vertices sample(const Mesh& mesh,const M4& frame,int limit,uint64_t cancel) {
    const int count=std::min(limit,int(mesh.vertices.rows())); Vertices points(count,3);
    for(int i=0;i<count;++i) { check_cancel(cancel); const int index=int(int64_t(i)*mesh.vertices.rows()/count);
        points.row(i)=point(frame,mesh.vertices.row(index)); }
    return points;
}
static void depths(const Surface& surface,const Vertices& points,const std::vector<int>& sides,double* output,int64_t* counts,uint64_t cancel) {
    counts[1]=0; counts[2]=0; counts[3]=0; counts[4]=-1; double deepest=-1;
    for(int i=0;i<points.rows();++i) {
        check_cancel(cancel); const V3 p=points.row(i); const Hit hit=nearest(surface,p); auto* row=output+8*i;
        row[0]=sides[size_t(i)]; row[1]=std::sqrt(hit.distance);
        ++counts[2-sides[size_t(i)]];
        if(sides[size_t(i)]>0&&row[1]>deepest) { deepest=row[1]; counts[4]=i; }
        std::copy(p.data(),p.data()+3,row+2); std::copy(hit.point.data(),hit.point.data()+3,row+5);
    }
}
static int inspect(const Mesh& source,const M4& a,const Mesh& volume,const M4& b,int limit,double* rows,int64_t* count,uint64_t cancel) {
    if(limit<1||limit>512||!a.allFinite()||!b.allFinite()||!rows||!count) throw std::runtime_error("Invalid bounded volume inspection.");
    const Vertices points=sample(source,a,limit,cancel),vertices=world_vertices(volume,b,cancel);
    auto faces=volume.triangles; if(b.block<3,3>(0,0).determinant()<0) faces.col(1).swap(faces.col(2));
    const auto token=cancel?&reinterpret_cast<Cancellation*>(cancel)->cancelled:nullptr; std::vector<int> sides;
    *count=points.rows(); const int status=boolean::classify(vertices,faces,points,sides,token);
    if(status==0) depths(Surface(volume,b),points,sides,rows,count,cancel);
    return status;
}
}
int af_inspection_volume(uint64_t source,const double* a,uint64_t volume,const double* b,int limit,double* rows,int64_t* count,uint64_t cancel) {
    try { return af::inspection::inspect(*af::mesh(source),af::M4(a),*af::mesh(volume),af::M4(b),limit,rows,count,cancel); }
    catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
