// SPDX-License-Identifier: GPL-3.0-or-later
// Positive uniform harmonic coordinates on a convex disk; geometry is untouched.
#include "surface_patch_internal.hpp"
#include <Eigen/SparseCholesky>

namespace af::curve_surface {
static double boundary_parameter(const PatchKey& key,const std::vector<double>& stations,int resolution) {
    const int count=int(stations.size())-1;
    if(key[0]==0) return key[1]<count?stations[size_t(key[1])]:-1;
    if(key[0]!=1) return -1;
    const auto a=key[1],b=key[2]; const double t=double(key[3])/resolution;
    if(b-a==1) return (1-t)*stations[size_t(a)]+t*stations[size_t(b)];
    if(a==0&&b==count-1) return t*stations[size_t(b)]+(1-t);
    return -1;
}
static std::vector<std::set<int>> neighbors(const Patch& patch) {
    std::vector<std::set<int>> result(patch.points.size());
    for(const auto& face:patch.faces) for(size_t j=0;j<face.size();++j) {
        const int a=int(face[j]),b=int(face[(j+1)%face.size()]);
        result[size_t(a)].insert(b); result[size_t(b)].insert(a);
    }
    return result;
}
static std::vector<int> boundary(Patch& patch,const Row& row,int resolution) {
    const auto positions=stations(row); std::vector<int> unknown; int next=0;
    for(const auto& key:patch.keys) {
        const double parameter=boundary_parameter(key,positions,resolution);
        unknown.push_back(parameter<0?next++:-1);
        const double angle=2*std::acos(-1.0)*parameter;
        patch.coordinates.emplace_back(parameter<0?V2::Zero().eval():V2(std::cos(angle),std::sin(angle)));
    }
    return unknown;
}
static void solve(Patch& patch,const std::vector<int>& unknown,uint64_t cancel) {
    const auto edges=neighbors(patch); const int count=*std::max_element(unknown.begin(),unknown.end())+1;
    if(!count) return;
    std::vector<Eigen::Triplet<double>> entries; Eigen::MatrixXd rhs=Eigen::MatrixXd::Zero(count,2);
    for(size_t i=0;i<unknown.size();++i) if(unknown[i]>=0) {
        check_cancel(cancel); entries.emplace_back(unknown[i],unknown[i],double(edges[i].size()));
        for(int j:edges[i]) if(unknown[size_t(j)]>=0) entries.emplace_back(unknown[i],unknown[size_t(j)],-1);
        else rhs.row(unknown[i])+=patch.coordinates[size_t(j)];
    }
    Eigen::SparseMatrix<double> matrix(count,count); matrix.setFromTriplets(entries.begin(),entries.end());
    Eigen::SimplicialLDLT<Eigen::SparseMatrix<double>> factor(matrix); const Eigen::MatrixXd result=factor.solve(rhs);
    if(factor.info()!=Eigen::Success||!result.allFinite()) throw std::runtime_error("Patch material parameterization failed.");
    for(size_t i=0;i<unknown.size();++i) if(unknown[i]>=0) { check_cancel(cancel); patch.coordinates[i]=result.row(unknown[i]); }
}
void patch_coordinates(Patch& patch,const Row& row,int resolution,uint64_t cancel) {
    const auto unknown=boundary(patch,row,resolution); solve(patch,unknown,cancel);
}
}
