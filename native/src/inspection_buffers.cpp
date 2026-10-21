#include "inspection_internal.hpp"

namespace af::inspection {
static V3 color(double value) {
    const V3 blue(.10,.30,1),yellow(1,.85,.15),red(1,.10,.06);
    return value<.5?V3(blue+(yellow-blue)*(2*value)):V3(yellow+(red-yellow)*(2*value-1));
}
static void triangle(Comparison& out,const Vertices& deltas,int face) {
    const auto& mesh=*out.target; const auto ids=mesh.triangles.row(face);
    const V3 a=mesh.vertices.row(ids[0]),b=mesh.vertices.row(ids[1]),c=mesh.vertices.row(ids[2]);
    V3 normal=(b-a).cross(c-a); if(normal.norm()>0) normal.normalize();
    for(int j=0;j<3;++j) {
        const V3 p=mesh.vertices.row(ids[j]),rgb=color(out.stats[1]>0?deltas.row(ids[j]).norm()/out.stats[1]:0);
        auto& row=out.chunks.back();
        for(const auto& v:std::array<V3,3>{p,normal,rgb}) for(int k=0;k<3;++k) row.push_back(float(v[k]));
        row.push_back(1);
    }
}
void buffers(Comparison& out,const Vertices& deltas,uint64_t cancel) {
    for(int face=0;face<out.target->triangles.rows();++face) {
        check_cancel(cancel);
        if(face%4096==0) { out.chunks.emplace_back(); out.chunks.back().reserve(4096*30); }
        triangle(out,deltas,face);
    }
}
}
