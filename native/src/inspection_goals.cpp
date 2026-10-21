#include "anthroforge/inspection_goals.h"
#include "inspection_internal.hpp"
#include "tissue_relaxation.hpp"

namespace af::inspection {
static V3 goal(const Mesh& mesh,const Mesh& rest,const Vertices& normals,const AfTissueRegion& region,
               int triangle,const V3& bary,uint64_t cancel) {
    Vertices goals(rest.vertices.rows(),3);
    for(int64_t i=0;i<goals.rows();++i) {
        check_cancel(cancel); goals.row(i)=tissue::region_goal(rest,normals,region,i);
    }
    return mapped_sample(rest,mesh,goals,false,triangle,bary,cancel);
}
static void row(const V3& goal,const V3& actual,const M4& frame,double* row) {
    const V3 a=point(frame,goal),b=point(frame,actual);
    std::copy_n(a.data(),3,row); std::copy_n(b.data(),3,row+3); row[6]=(b-a).norm();
}
}
int af_inspection_goals(uint64_t target,uint64_t rest,const AfTissueSource* source,
    int triangle,const double* bary,const double* frame,const AfTissueRegion* regions,
    int count,double* rows,uint64_t cancel) {
    try {
        if(!source||!bary||!frame||count<0||count>1024||(count&&(!regions||!rows)))
            throw std::runtime_error("Invalid constraint goal inspection inputs.");
        const auto mesh=af::mesh(target),reference=af::mesh(rest); const af::M4 m(frame);
        af::inspection::witness(*mesh,triangle,af::V3(bary));
        const auto normals=af::tissue::source_normals(*reference,*source,cancel);
        const auto actual=af::inspection::sample(*mesh,mesh->vertices,triangle,af::V3(bary));
        for(int i=0;i<count;++i) af::inspection::row(af::inspection::goal(*mesh,*reference,normals,
            regions[i],triangle,af::V3(bary),cancel),actual,m,rows+7*i);
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
