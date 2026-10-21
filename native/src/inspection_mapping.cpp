#include "inspection_internal.hpp"

namespace af::inspection {
bool canonical(const Mesh& a,const Mesh& b) {
    return a.vertices.rows()==b.vertices.rows()&&a.corners==b.corners&&a.offsets==b.offsets&&
        a.tissue.kind==b.tissue.kind&&a.tissue.offsets==b.tissue.offsets&&a.tissue.indices==b.tissue.indices&&
        a.tissue.weights==b.tissue.weights&&a.tissue.sides==b.tissue.sides&&same_basis(a.basis,b.basis);
}
V3 source_point(const Mesh& mesh,const Mesh& base,int64_t vertex) {
    const auto& d=mesh.tissue;
    if(!d.kind||d.source_count!=base.vertices.rows()) throw std::runtime_error("Source material samples do not match.");
    V3 result=V3::Zero();
    for(auto j=d.offsets.at(size_t(vertex));j<d.offsets.at(size_t(vertex)+1);++j)
        result+=base.vertices.row(d.indices[size_t(j)]).transpose()*d.weights[size_t(j)];
    return result;
}
static Mesh field_mesh(const Mesh& source,const Vertices& values) {
    Mesh result; result.vertices=values; result.tissue=source.tissue;
    result.offsets=source.offsets; result.corners=source.corners; return result;
}
Vertices mapped(const Mesh& reference,const Mesh& target,const Vertices& values,bool source,uint64_t cancel) {
    if(values.rows()!=reference.vertices.rows()) throw std::runtime_error("Inspection field has incompatible samples.");
    if(!source&&canonical(reference,target)) return values;
    if(!source&&(!reference.tissue.kind||!target.tissue.kind||reference.tissue.source_count!=target.tissue.source_count))
        throw std::runtime_error("Stages have no compatible material correspondence.");
    auto field=field_mesh(reference,values); Vertices result(target.vertices.rows(),3);
    if(source) for(int64_t i=0;i<result.rows();++i) { check_cancel(cancel); result.row(i)=source_point(target,field,i); }
    else {
        const auto index=binding::index(field,cancel);
        for(int64_t i=0;i<result.rows();++i) { check_cancel(cancel);
            result.row(i)=binding::material_point(index,binding::weights(target.tissue,i),target.tissue.sides[size_t(i)],cancel); }
    }
    return result;
}
void witness(const Mesh& mesh,int triangle,const V3& bary) {
    if(triangle<0||triangle>=mesh.triangles.rows()||!bary.allFinite()||bary.minCoeff()<-1e-8||std::abs(bary.sum()-1)>1e-8)
        throw std::runtime_error("Invalid inspection surface witness.");
}
V3 mapped_sample(const Mesh& reference,const Mesh& target,const Vertices& values,bool source,int triangle,const V3& bary,uint64_t cancel) {
    witness(target,triangle,bary); check_cancel(cancel);
    if(!source&&canonical(reference,target)) return sample(target,values,triangle,bary);
    if(source) {
        const auto field=field_mesh(reference,values); V3 result=V3::Zero();
        for(int j=0;j<3;++j) result+=source_point(target,field,target.triangles(triangle,j))*bary[j];
        return result;
    }
    const auto field=field_mesh(reference,values); const auto index=binding::index(field,cancel); V3 result=V3::Zero();
    for(int j=0;j<3;++j) {
        const auto id=target.triangles(triangle,j); check_cancel(cancel);
        result+=binding::material_point(index,binding::weights(target.tissue,id),target.tissue.sides[size_t(id)],cancel)*bary[j];
    }
    return result;
}
V3 sample(const Mesh& mesh,const Vertices& values,int triangle,const V3& bary) {
    witness(mesh,triangle,bary); V3 result=V3::Zero();
    for(int j=0;j<3;++j) result+=values.row(mesh.triangles(triangle,j)).transpose()*bary[j];
    return result;
}
}
