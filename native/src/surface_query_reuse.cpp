// SPDX-License-Identifier: GPL-3.0-or-later
#include "surface_query.hpp"
#include "../boolean/qualification.hpp"

namespace af::query {
static bool unchanged_face(const Input& input,int face,const Mesh& source,int64_t original) {
    for(int j=0;j<3;++j) {
        const auto a=input.vertices.row(input.faces(face,j));
        const auto b=source.vertices.row(source.triangles(original,j));
        if(!(a.array()==b.array()).all()) return false;
    }
    return true;
}
static std::vector<uint8_t> original_faces(const Input& input,const Mesh& source,uint64_t cancel) {
    std::vector<uint8_t> mask(input.faces.rows()),seen(source.triangles.rows()); size_t count=0;
    for(int i=0;i<input.faces.rows();++i) {
        check_cancel(cancel); const auto original=input.origins.at(size_t(i));
        if(original<0) continue;
        if(original>=source.triangles.rows()||seen[size_t(original)]||!unchanged_face(input,i,source,original)) return {};
        mask[size_t(i)]=1; seen[size_t(original)]=1; ++count;
    }
    return count==seen.size()?mask:std::vector<uint8_t>{};
}
bool reusable(const Input& input,const Mesh& source,uint64_t cancel) {
    const auto mask=original_faces(input,source,cancel);
    if(mask.empty()) return false;
    const auto token=cancel?&reinterpret_cast<Cancellation*>(cancel)->cancelled:nullptr;
    return boolean::qualify(input.vertices,input.faces,mask,token)==boolean::Suitability::Reusable;
}
}
