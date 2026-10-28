#include "anthroforge/inspection.h"
#include "mesh_internal.hpp"
#include "surface_query.hpp"

namespace af::inspection {
static Hit placement_hit(const Mesh& mesh,const M4& frame,const V3& start,const V3& ray,bool directional) {
    if(!directional) return nearest(Surface(mesh,frame),start);
    double row[10]; if(!pick_surface(mesh,frame,start,ray,row)) return {};
    return {int(row[2]),V3(row+4),V3(row+7),row[0]*row[0]};
}
static void placement_row(const std::shared_ptr<Mesh>& mesh,const M4& frame,const V3& start,
                          const V3& ray,bool directional,double offset,double* row) {
    const Hit hit=placement_hit(*mesh,frame,start,ray,directional);
    std::fill(row,row+16,0); row[0]=-1; if(hit.triangle<0) return;
    const auto source=query::original(mesh); const Surface material(*source,frame);
    const Hit original=query::material_hit(*mesh,material,hit);
    const V3 normal=surface_normal(*mesh,frame,hit.triangle);
    const V3 accepted=directional?surface_snap(*mesh,frame,hit.triangle,hit.point,offset):hit.point;
    row[0]=original.triangle; row[1]=std::sqrt(hit.distance);
    std::copy(hit.point.data(),hit.point.data()+3,row+2); std::copy(normal.data(),normal.data()+3,row+5);
    std::copy(accepted.data(),accepted.data()+3,row+8);
    row[11]=(start-hit.point).dot(normal); row[12]=directional?ray.normalized().dot(normal):0;
    row[13]=hit.triangle; row[14]=double(mesh->query_source!=nullptr); row[15]=(accepted-start).norm();
}
static int placements(int count,const uint64_t* handles,const double* frames,const double* request,int ray,double* rows,uint64_t cancel) {
    if(count<1||count>4096||!handles||!frames||!request||!rows) throw std::runtime_error("Placement inspection needs 1–4096 targets.");
    const V3 start(request),direction(request+3); int winner=-1; double distance=INFINITY;
    if(!start.allFinite()||!direction.allFinite()||!std::isfinite(request[6])||(ray&&direction.norm()<1e-15))
        throw std::runtime_error("Placement inspection needs a finite point and valid ray/offset.");
    for(int i=0;i<count;++i) {
        check_cancel(cancel); const M4 frame(frames+16*i); if(!frame.allFinite()) throw std::runtime_error("Invalid placement frame.");
        auto* row=rows+16*i; placement_row(mesh(handles[i]),frame,start,direction,ray!=0,request[6],row);
        if(row[0]>=0&&row[1]<distance) { distance=row[1]; winner=i; }
    }
    return winner;
}
}
int af_inspection_placement(int count,const uint64_t* handles,const double* frames,const double* request,int ray,double* rows,uint64_t cancel) {
    try { return af::inspection::placements(count,handles,frames,request,ray,rows,cancel); }
    catch(const std::exception& error) { af::set_error(error.what()); return -2; }
}
