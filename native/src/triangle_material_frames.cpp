// SPDX-License-Identifier: GPL-3.0-or-later
#include "material_chart.hpp"
#include <Eigen/QR>

namespace af::triangle_material {
using Key=std::array<int,3>;
using Lookup=std::map<Key,int>;
using Origins=std::map<int64_t,std::vector<int>>;
static Key key(Key indices) { std::sort(indices.begin(),indices.end()); return indices; }
static Lookup triangles(const Mesh& mesh,uint64_t cancel) {
    Lookup result;
    for(int i=0;i<mesh.triangles.rows();++i) {
        check_cancel(cancel); const auto row=mesh.triangles.row(i);
        result.emplace(key({row[0],row[1],row[2]}),i);
    }
    return result;
}
static Origins origins(const Mesh& mesh,uint64_t cancel) {
    Origins result;
    for(size_t i=0;i<mesh.triangle_material.origins.size();++i) {
        check_cancel(cancel); result[mesh.triangle_material.origins[i]].push_back(int(i));
    }
    return result;
}
static M3 coordinates(const Mesh& mesh,int triangle) {
    M3 result;
    const auto* data=mesh.triangle_material.coordinates.data()+9*triangle;
    for(int i=0;i<3;++i) result.row(i)=V3(data+3*i);
    return result;
}
static std::pair<int,M3> source(const Mesh& mesh,const Lookup& index,const double* record) {
    Key ids;
    for(int i=0;i<3;++i) {
        if(!std::isfinite(record[i])||record[i]<0||record[i]>=mesh.vertices.rows()||record[i]!=std::floor(record[i]))
            throw std::runtime_error("Invalid retained Boolean attachment triangle.");
        ids[size_t(i)]=int(record[i]);
    }
    const auto found=index.find(key(ids));
    if(found==index.end()) throw std::runtime_error("Missing retained Boolean material triangle.");
    const auto original=coordinates(mesh,found->second); M3 result;
    for(int i=0;i<3;++i) for(int j=0;j<3;++j)
        if(ids[size_t(i)]==mesh.triangles(found->second,j)) result.row(i)=original.row(j);
    return {found->second,result};
}
static material::Location locate(const Mesh& mesh,const Origins& index,int64_t origin,const V3& query,uint64_t cancel) {
    const auto found=index.find(origin);
    if(found!=index.end()) for(int triangle:found->second) {
        check_cancel(cancel); const M3 coords=coordinates(mesh,triangle);
        const V3 weights=coords.transpose().colPivHouseholderQr().solve(query);
        if(!weights.allFinite()||weights.minCoeff()<-1e-7||std::abs(weights.sum()-1)>1e-7) continue;
        if((coords.transpose()*weights-query).norm()>1e-7) continue;
        return {triangle,weights,coords};
    }
    throw std::runtime_error("Attachment material location is covered by the current union; restore its shape or explicitly rebind.");
}
static M4 resolve(const Mesh& before,const Mesh& after,const Lookup& lookup,const Origins& index,const M4& world,const double* record,uint64_t cancel) {
    const auto [triangle,coords]=source(before,lookup,record); const V3 weights(record+3);
    if(!weights.allFinite()||weights.minCoeff()<-1e-6||std::abs(weights.sum()-1)>1e-6)
        throw std::runtime_error("Invalid retained Boolean attachment coordinates.");
    const auto hit=locate(after,index,before.triangle_material.origins[size_t(triangle)],coords.transpose()*weights,cancel);
    material::Tangents directions;
    directions.col(0)=coords.row(1)-coords.row(0); directions.col(1)=coords.row(2)-coords.row(0);
    return material::frame(after,hit,directions,world,record);
}
void frames(const Mesh& before,const Mesh& after,const M4& world,int count,const double* records,double* output,uint64_t cancel) {
    if(!before.triangle_material.source_count||before.triangle_material.source_count!=after.triangle_material.source_count)
        throw std::runtime_error("Boolean source topology changed; explicitly rebind.");
    const auto lookup=triangles(before,cancel); const auto index=origins(after,cancel);
    for(int i=0;i<count;++i) {
        check_cancel(cancel); Eigen::Map<M4> frame(output+16*i);
        frame=resolve(before,after,lookup,index,world,records+28*i,cancel);
    }
}
}
