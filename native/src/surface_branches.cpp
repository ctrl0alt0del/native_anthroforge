// SPDX-License-Identifier: GPL-3.0-or-later
// Native port of addon branched_surface.py assembly; explicit shared vertex IDs.
#include "surface_branch_internal.hpp"
#include <numeric>

namespace af::curve_surface {
void append_faces(Assembly& assembly,const std::vector<uint32_t>& mapping,size_t rows,size_t columns,bool flip) {
    for(size_t i=0;i+1<rows;++i) for(size_t j=0;j+1<columns;++j) {
        const size_t a=i*columns+j;
        std::vector<int64_t> face{mapping[a],mapping[a+columns],mapping[a+columns+1],mapping[a+1]};
        if(flip) std::reverse(face.begin(),face.end());
        assembly.faces.push_back(std::move(face));
    }
}
Assembly main_assembly(const Rows& rows,const std::vector<Branch>& branches,bool exact,int strips,int samples,uint64_t cancel) {
    Assembly result; result.along=merged_stations(rows,exact,0,samples);
    for(const auto& branch:branches) result.along.insert(result.along.end(),branch.roots.begin(),branch.roots.end());
    result.along=unique_stations(std::move(result.along));
    const auto source=uniform_stations(rows.size());
    auto across=uniform_stations(strips>0?1+(rows.size()-1)*size_t(strips):17);
    across.insert(across.end(),source.begin(),source.end()); across=unique_stations(std::move(across));
    result.main=across_grid(sampled_grid(rows,result.along,cancel),source,across,cancel);
    result.points=result.main.points; return result;
}
static Rows branch_rows(const Rows& rows,const Branch& branch) {
    Rows result;
    for(int row:branch.rows) result.push_back(rows[size_t(row)]);
    return result;
}
static std::vector<double> normalized(const std::vector<double>& values,double start,double end) {
    std::vector<double> result;
    for(double value:values) result.push_back((value-start)/(end-start));
    return result;
}
static Grid branch_grid(const Rows& rows,const Branch& branch,const std::vector<double>& seam,bool exact,int samples,uint64_t cancel) {
    const auto children=branch_rows(rows,branch);
    const auto along=merged_stations(children,exact,17,samples);
    const auto roots=normalized(branch.roots,branch.roots.front(),branch.roots.back());
    const auto across=normalized(seam,branch.roots.front(),branch.roots.back());
    return across_grid(sampled_grid(children,along,cancel),roots,across,cancel);
}
static std::vector<uint32_t> append_vertices(Assembly& assembly,const Grid& grid,size_t seam,size_t boundary,const std::vector<double>& along,uint64_t cancel) {
    budget(assembly.points.size()+grid.rows*(grid.columns-1),2*(assembly.faces.size()+(grid.rows-1)*(grid.columns-1)));
    std::vector<uint32_t> mapping;
    for(size_t i=0;i<grid.rows;++i) {
        const size_t shared=boundary*assembly.main.columns+seam+i;
        const V3 correction=assembly.main.points[shared]-grid.points[i*grid.columns];
        mapping.push_back(uint32_t(shared));
        for(size_t j=1;j<grid.columns;++j) {
            check_cancel(cancel); const double t=along[j],smooth=t*t*(3-2*t);
            mapping.push_back(uint32_t(assembly.points.size()));
            assembly.points.push_back(grid.points[i*grid.columns+j]+(1-smooth)*correction);
        }
    }
    return mapping;
}
void append_branch(Assembly& assembly,const Rows& rows,const Branch& branch,bool exact,int samples,uint64_t cancel) {
    const auto first=std::lower_bound(assembly.along.begin(),assembly.along.end(),branch.roots.front());
    const auto last=std::upper_bound(first,assembly.along.end(),branch.roots.back());
    const auto grid=branch_grid(rows,branch,std::vector<double>(first,last),exact,samples,cancel);
    const auto along=merged_stations(branch_rows(rows,branch),exact,17,samples);
    const size_t boundary=branch.boundary==0?0:assembly.main.rows-1;
    const auto mapping=append_vertices(assembly,grid,size_t(first-assembly.along.begin()),boundary,along,cancel);
    append_faces(assembly,mapping,grid.rows,grid.columns,(branch.boundary!=0)!=assembly.flip);
}
static std::shared_ptr<Mesh> build(const Rows& rows,int main_count,const std::vector<Branch>& branches,bool exact,int strips,int samples,bool flip,uint64_t cancel) {
    auto assembly=main_assembly(Rows(rows.begin(),rows.begin()+main_count),branches,exact,strips,samples,cancel);
    assembly.flip=flip;
    std::vector<uint32_t> mapping(assembly.points.size()); std::iota(mapping.begin(),mapping.end(),0);
    append_faces(assembly,mapping,assembly.main.rows,assembly.main.columns,flip);
    for(const auto& branch:branches) append_branch(assembly,rows,branch,exact,samples,cancel);
    return make_mesh(assembly.points,assembly.faces,cancel,false);
}
}
uint64_t af_curve_surface_branches(const AfSurfaceRow* data,int count,int main_count,const AfSurfaceBranch* connections,int branch_count,int exact,int strips,int flip,uint64_t cancel) {
    try {
        if(strips<0||strips>256) throw std::runtime_error("Invalid branch strip count.");
        const auto rows=af::curve_surface::inputs(data,count,true,cancel);
        const auto branches=af::curve_surface::branch_inputs(rows,main_count,connections,branch_count);
        int samples=2; for(int i=0;i<count;++i) samples=std::max(samples,data[i].samples);
        return af::retain(af::curve_surface::build(rows,main_count,branches,exact!=0,strips,samples,flip!=0,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
