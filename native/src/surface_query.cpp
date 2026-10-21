// SPDX-License-Identifier: GPL-3.0-or-later
#include "surface_query.hpp"
#include "construction_internal.hpp"
#include "../boolean/exterior.hpp"

namespace af::query {
std::shared_ptr<Mesh> original(const std::shared_ptr<Mesh>& source) {
    return source->query_source?source->query_source:source;
}
static std::shared_ptr<Mesh> selectable(const boolean::Exterior& output,const Input& input,uint64_t cancel) {
    Points vertices; Faces faces; std::vector<int64_t> origins;
    for(int i=0;i<output.vertices.rows();++i) vertices.push_back(output.vertices.row(i));
    for(int i=0;i<output.faces.rows();++i) {
        check_cancel(cancel); const auto source=input.origins.at(size_t(output.origins[i]));
        if(source<0) continue;
        const auto f=output.faces.row(i); const V3 a=vertices[f[1]]-vertices[f[0]],b=vertices[f[2]]-vertices[f[0]];
        if(a.cross(b).squaredNorm()==0) continue;
        faces.push_back({f[0],f[1],f[2]}); origins.push_back(source);
    }
    auto result=make_mesh(vertices,faces,cancel,true); result->query_faces=std::move(origins); return result;
}
std::shared_ptr<Mesh> confirmed(const std::shared_ptr<Mesh>& source,const Mesh* base,uint64_t cancel) {
    check_cancel(cancel);
    if(source->query_source) throw std::runtime_error("A query copy cannot be used as original geometry.");
    if(!source->prepared) throw std::runtime_error("Confirmed placement requires accepted prepared geometry.");
    const auto input=close(*source,base,cancel);
    const auto output=boolean::exterior(input.vertices,input.faces,cancel?&reinterpret_cast<Cancellation*>(cancel)->cancelled:nullptr);
    auto result=selectable(output,input,cancel); result->query_source=source;
    return result;
}
Hit material_hit(const Mesh& proxy,const Surface& source,Hit hit) {
    if(!proxy.query_source) return hit;
    hit.triangle=int(proxy.query_faces.at(size_t(hit.triangle)));
    const auto face=source.triangles->row(hit.triangle);
    hit.weights=barycentric(hit.point,source.vertices.row(face[0]),source.vertices.row(face[1]),source.vertices.row(face[2]));
    if(hit.weights.minCoeff()<-1e-7||hit.weights.maxCoeff()>1+1e-7)
        throw std::runtime_error("Confirmed surface correspondence is numerically ambiguous.");
    hit.weights=hit.weights.cwiseMax(0); hit.weights/=hit.weights.sum();
    hit.point.setZero();
    for(int i=0;i<3;++i) hit.point+=hit.weights[i]*source.vertices.row(face[i]).transpose();
    return hit;
}
}
uint64_t af_surface_query(uint64_t handle,uint64_t base,int confirmed,uint64_t cancel) {
    try {
        auto source=af::mesh(handle); af::check_cancel(cancel);
        if(confirmed==0) return af::retain(source);
        if(confirmed!=1) throw std::runtime_error("Unknown surface query mode.");
        auto backing=base?af::mesh(base):nullptr;
        return af::retain(af::query::confirmed(source,backing.get(),cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
