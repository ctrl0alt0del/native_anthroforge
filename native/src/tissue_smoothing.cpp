// SPDX-License-Identifier: GPL-3.0-or-later
#include "construction_internal.hpp"
#include "anthroforge/tissue.h"
#include "af_smoothing/height.h"
#include "material_domain.hpp"
#include "tissue_height.hpp"
#include "mesh_quality.hpp"

namespace af::tissue {
static void compatible(const Mesh& base,const Mesh& own,int count) {
    if(count<1||material_grids(base).size()!=size_t(count)||base.vertices.rows()!=own.vertices.rows()||own.tissue.kind!=4||
       base.corners!=own.corners||base.offsets!=own.offsets)
        throw std::runtime_error("Height smoothing requires a full, uncomposed material side.");
}
static std::vector<int64_t> triangle_labels(const Mesh& mesh) {
    std::vector<int64_t> result;
    for(const auto face:mesh.polygons) result.push_back(mesh.tissue.parts.at(size_t(face)));
    return result;
}
static void metrics(const AF_HeightReport& r,double* out) {
    const double values[]={double(r.iterations),double(r.samples),double(r.pinned),
        double(r.skipped_triangles),r.total_ms,r.solve_ms,r.violation,r.stationarity,
        r.complementarity,r.max_change,r.complementarity_relative,r.objective};
    std::copy(values,values+12,out);
    out[12]=r.status;
}
static Vertices smooth_part(const Mesh& base,const Vertices& own,const std::vector<int64_t>& faces,
                           const std::vector<int64_t>& labels,int part,const double* settings,double* report) {
    AF_HeightReport result{};
    auto output=smooth_heights(base.vertices,own,faces,labels,part,settings,result);
    metrics(result,report);
    return output;
}
static std::shared_ptr<Mesh> smooth(const Mesh& base,const Mesh& own,const double* settings,int count,double* reports,uint64_t cancel) {
    compatible(base,own,count); auto vertices=own.vertices;
    for(int i=0;i<count*4;++i) if(!std::isfinite(settings[i])||settings[i]<0)
        throw std::runtime_error("Height smoothing settings must be finite and nonnegative.");
    const std::vector<int64_t> faces(base.triangles.data(),base.triangles.data()+base.triangles.size());
    const auto labels=triangle_labels(own);
    for(int part=0;part<count;++part) {
        check_cancel(cancel); const auto* s=settings+part*4; auto* report=reports+part*13;
        if(s[0]==0||s[1]==0||s[2]==0||s[3]==0) continue;
        vertices=smooth_part(base,vertices,faces,labels,part,s+1,report);
        check_cancel(cancel);
    }
    auto result=deform_mesh(own,vertices,cancel,true);
    quality::validate_tissue(own,*result,cancel);
    return result;
}
}
uint64_t af_tissue_smooth_diagnostics(uint64_t base,uint64_t own,const double* settings,int count,double* reports,uint64_t cancel) {
    try {
        if(!settings||!reports||count<1||count>256) throw std::runtime_error("Invalid smoothing settings or reports.");
        std::fill(reports,reports+count*13,0.0);
        return af::retain(af::tissue::smooth(*af::mesh(base),*af::mesh(own),settings,count,reports,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_tissue_smooth(uint64_t base,uint64_t own,const double* settings,int count,double* reports,uint64_t cancel) {
    try {
        if(!reports||count<1||count>256) throw std::runtime_error("Invalid smoothing reports.");
        std::vector<double> complete(size_t(count)*13);
        const auto result=af_tissue_smooth_diagnostics(base,own,settings,count,complete.data(),cancel);
        if(result) for(int i=0;i<count;++i) std::copy_n(complete.data()+i*13,12,reports+i*12);
        return result;
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
