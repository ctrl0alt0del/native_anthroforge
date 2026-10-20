// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_envelope.hpp"

namespace af::tissue {
static int64_t origin(const TissueDomain& d,int64_t vertex) {
    const auto start=d.offsets[size_t(vertex)];
    if(d.offsets[size_t(vertex+1)]!=start+1||d.weights[size_t(start)]!=1)
        throw std::runtime_error("Envelope cropping requires full, uncropped material sides.");
    return d.indices[size_t(start)];
}
static Vertices first_side(const Mesh& base,const Mesh& own,uint64_t cancel) {
    auto values=base.vertices; std::vector<bool> used(size_t(values.rows()),false);
    for(int64_t i=0;i<own.vertices.rows();++i) if(own.tissue.sides[size_t(i)]!=2) {
        check_cancel(cancel); const auto index=origin(own.tissue,i);
        values.row(index)=own.vertices.row(i); used[size_t(index)]=true;
    }
    if(std::find(used.begin(),used.end(),false)!=used.end())
        throw std::runtime_error("Envelope cropping requires every original material sample.");
    return values;
}
static Vertices second_side(const Vertices& first,const Mesh& own,uint64_t cancel) {
    auto values=first;
    for(int64_t i=0;i<own.vertices.rows();++i) if(own.tissue.sides[size_t(i)]==2) {
        check_cancel(cancel); values.row(origin(own.tissue,i))=own.vertices.row(i);
    }
    return values;
}
static TissueDomain domain(const Mesh& base,const Mesh& own) {
    auto d=tissue_identity(4,base.vertices.rows(),int64_t(base.offsets.size())-1);
    for(size_t i=0;i<own.tissue.faces.size();++i) {
        const auto face=own.tissue.faces[i];
        if(face<0||face>=int64_t(d.parts.size())) throw std::runtime_error("Invalid envelope material face.");
        d.parts[size_t(face)]=own.tissue.parts[i];
    }
    return d;
}
static bool reversed(const Mesh& base,const Mesh& own) {
    if(own.corners.empty()) return false;
    const auto face=own.tissue.faces[0];
    return origin(own.tissue,own.corners[0])!=base.corners[size_t(base.offsets[size_t(face)])];
}
std::shared_ptr<Mesh> crop_envelope(const Mesh& base,const Mesh& own,const double* plane,uint64_t cancel) {
    const auto first=first_side(base,own,cancel),second=second_side(first,own,cancel);
    auto a=deform_mesh(base,first,cancel,false),b=deform_mesh(base,second,cancel,false);
    a->tissue=b->tissue=domain(base,own);
    a->basis=b->basis=material_basis(base);
    a=crop_material(base,*a,plane,cancel); b=crop_material(base,*b,plane,cancel);
    return compose_envelope(*a,*b,reversed(base,own),cancel);
}
}
