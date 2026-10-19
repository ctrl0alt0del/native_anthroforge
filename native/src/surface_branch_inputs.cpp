// SPDX-License-Identifier: GPL-3.0-or-later
// Addon branched_surface.py constraints; see migration/CURVE_SURFACES.md.
#include "surface_branch_internal.hpp"
#include <set>

namespace af::curve_surface {
static double root_station(const Row& row,int point) {
    const auto positions=stations(row);
    for(size_t i=1;i<row.parameters.size();++i) {
        const double a=row.parameters[i-1],b=row.parameters[i];
        if(point>=std::min(a,b)&&point<=std::max(a,b)&&a!=b) {
            const double t=(point-a)/(b-a);
            return (1-t)*positions[i-1]+t*positions[i];
        }
    }
    throw std::runtime_error("Branch root is outside the consumed authored path range.");
}
static void append_root(Branch& result,const Rows& rows,const AfSurfaceBranch& input,int i) {
    const int child=input.rows[i];
    if(child<0||size_t(child)>=rows.size()) throw std::runtime_error("Invalid branch source row.");
    const double root=root_station(rows[input.boundary],input.roots[i]);
    if(root<=0||root>=1||(!result.roots.empty()&&root<=result.roots.back()))
        throw std::runtime_error("Branch roots must be strictly ordered interior main points.");
    const V3 parent=sample(rows[input.boundary],stations(rows[input.boundary]),root);
    if(!parent.isApprox(rows[child].points.front(),1e-8)&&(parent-rows[child].points.front()).norm()>1e-8)
        throw std::runtime_error("Branch endpoint must equal its explicit shared main point.");
    result.rows.push_back(child); result.roots.push_back(root);
}
static Branch read_branch(const Rows& rows,int main_count,const AfSurfaceBranch& input) {
    if((input.boundary!=0&&input.boundary!=main_count-1)||input.count<2||input.count>1024||!input.rows||!input.roots)
        throw std::runtime_error("A branch requires an outer main curve and at least two roots.");
    Branch result; result.boundary=input.boundary;
    for(int i=0;i<input.count;++i) append_root(result,rows,input,i);
    return result;
}
static void validate_branch(const Branch& branch,const std::vector<Branch>& previous,int main_count,std::set<int>& used) {
    for(int row:branch.rows)
        if(row<main_count||!used.insert(row).second) throw std::runtime_error("Branch sources must be distinct from main and other branches.");
    for(const auto& other:previous)
        if(branch.boundary==other.boundary&&branch.roots.front()<=other.roots.back()&&branch.roots.back()>=other.roots.front())
            throw std::runtime_error("Branch intervals cannot overlap or share endpoints.");
}
std::vector<Branch> branch_inputs(const Rows& rows,int main_count,const AfSurfaceBranch* data,int count) {
    if(main_count<2||size_t(main_count)>rows.size()||!data||count<1||count>512)
        throw std::runtime_error("Invalid branched surface sources.");
    for(const auto& row:rows) if(row.closed) throw std::runtime_error("Branched surfaces require open paths.");
    std::vector<Branch> result; std::set<int> used;
    for(int i=0;i<count;++i) {
        auto branch=read_branch(rows,main_count,data[i]);
        validate_branch(branch,result,main_count,used); result.push_back(std::move(branch));
    }
    if(used.size()+size_t(main_count)!=rows.size()) throw std::runtime_error("Every branch source must have an explicit root.");
    return result;
}
}
