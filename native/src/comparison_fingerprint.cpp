#include "mesh_internal.hpp"
#include "path_internal.hpp"
#include <algorithm>
#include <array>
#include <cstring>

namespace af {
struct Fingerprint {
    uint64_t first=14695981039346656037ULL, second=7809847782465536322ULL;
    void word(uint64_t value) {
        for(int i=0;i<8;++i) {
            const auto byte=(value>>(i*8))&255;
            first=(first^byte)*1099511628211ULL; second=(second^byte)*1099511628211ULL;
        }
    }
    void real(double value) {
        if(value==0) value=0; // Canonicalize negative zero, preserving numerical equality.
        uint64_t bits=0; std::memcpy(&bits,&value,sizeof(bits)); word(bits);
    }
};
static std::vector<std::array<int,3>> oriented(const Mesh& mesh,uint64_t cancel) {
    std::vector<std::array<int,3>> rows; rows.reserve(size_t(mesh.triangles.rows()));
    for(int i=0;i<mesh.triangles.rows();++i) {
        check_cancel(cancel); std::array<int,3> row{mesh.triangles(i,0),mesh.triangles(i,1),mesh.triangles(i,2)};
        const auto minimum=std::min_element(row.begin(),row.end());
        std::rotate(row.begin(),minimum,row.end()); rows.push_back(row);
    }
    std::sort(rows.begin(),rows.end()); check_cancel(cancel); return rows;
}
static Fingerprint mesh_fingerprint(const Mesh& mesh,uint64_t cancel) {
    Fingerprint out; out.word(uint64_t(mesh.vertices.rows())); out.word(uint64_t(mesh.triangles.rows()));
    for(int64_t i=0;i<mesh.vertices.size();++i) {
        if(i%4096==0) check_cancel(cancel); out.real(mesh.vertices.data()[i]);
    }
    for(const auto& row:oriented(mesh,cancel)) for(int index:row) out.word(uint64_t(index));
    return out;
}
static Fingerprint path_fingerprint(const Path& path,uint64_t cancel) {
    Fingerprint out; out.word(uint64_t(path.samples.size())); out.word(path.closed);
    for(size_t i=0;i<path.samples.size();++i) {
        if(i%4096==0) check_cancel(cancel); out.real(path.samples[i]);
    }
    return out;
}
}
int af_comparison_fingerprint(uint64_t handle,int path,uint64_t* output,uint64_t cancel) {
    try {
        const auto value=path?af::path_fingerprint(*af::path(handle),cancel):af::mesh_fingerprint(*af::mesh(handle),cancel);
        output[0]=value.first; output[1]=value.second; return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
