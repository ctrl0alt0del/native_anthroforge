// SPDX-License-Identifier: GPL-3.0-or-later
#include "construction_internal.hpp"
#include "anthroforge/tissue.h"
#include "af_smoothing/height.h"
#include "material_domain.hpp"

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
}
static Vertices smooth_part(const Mesh& base,const Vertices& own,const std::vector<int64_t>& faces,
                           const std::vector<int64_t>& labels,int part,const double* settings,double* report) {
    Vertices output(own.rows(),3); AF_HeightReport result{};
    const int code=af_height_smooth(base.vertices.data(),own.data(),int(own.rows()),faces.data(),
        int(labels.size()),3,labels.data(),part,settings[0],settings[1],settings[2],output.data(),&result);
    metrics(result,report);
    if(code) throw std::runtime_error(std::string("Height smoothing: ")+result.message);
    return output;
}
static std::shared_ptr<Mesh> smooth(const Mesh& base,const Mesh& own,const double* settings,int count,double* reports,uint64_t cancel) {
    compatible(base,own,count); auto vertices=own.vertices;
    for(int i=0;i<count*4;++i) if(!std::isfinite(settings[i])||settings[i]<0)
        throw std::runtime_error("Height smoothing settings must be finite and nonnegative.");
    const std::vector<int64_t> faces(base.triangles.data(),base.triangles.data()+base.triangles.size());
    const auto labels=triangle_labels(own);
    for(int part=0;part<count;++part) {
        check_cancel(cancel); const auto* s=settings+part*4; auto* report=reports+part*12;
        if(s[0]==0||s[1]==0||s[2]==0||s[3]==0) continue;
        vertices=smooth_part(base,vertices,faces,labels,part,s+1,report);
        check_cancel(cancel);
    }
    return deform_mesh(own,vertices,cancel,true);
}
}
uint64_t af_tissue_smooth(uint64_t base,uint64_t own,const double* settings,int count,double* reports,uint64_t cancel) {
    try {
        if(!settings||!reports||count<1) throw std::runtime_error("Missing smoothing settings or reports.");
        std::fill(reports,reports+count*12,0.0);
        return af::retain(af::tissue::smooth(*af::mesh(base),*af::mesh(own),settings,count,reports,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
