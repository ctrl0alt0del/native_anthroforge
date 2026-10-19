// SPDX-License-Identifier: GPL-3.0-or-later
// Shared material IDs define seams; coordinates never infer a connection.
#include "tissue_branches.hpp"
#include <unordered_map>

namespace af::tissue {
static Connection connection(const MaterialGrid& main,const MaterialGrid& branch,const double* settings) {
    if(main.rows<3||branch.rows<2||branch.columns<3) throw std::runtime_error("Branch connectors need at least three cross/along samples.");
    Connection result; result.width=settings[0]; result.fullness=settings[1];
    if(!std::isfinite(result.width)||result.width<=0||result.width>=.5||!std::isfinite(result.fullness))
        throw std::runtime_error("Connector width must be between zero and one half; fullness must be finite.");
    std::unordered_map<int64_t,int> indices;
    for(size_t i=0;i<main.indices.size();++i) indices[main.indices[i]]=int(i);
    for(int i=0;i<branch.rows;++i) {
        const auto found=indices.find(branch.indices[size_t(i*branch.columns)]);
        if(found==indices.end()) throw std::runtime_error("Branch root has no explicit main material identity.");
        const int row=found->second/main.columns; if(i&&row!=result.boundary) throw std::runtime_error("Branch seam crosses main boundaries.");
        result.boundary=row; result.seam.push_back(found->second%main.columns);
    }
    result.across=branch.across; result.along=branch.along; return result;
}
static void validate(const Connection& c,const MaterialGrid& main) {
    if(c.boundary!=0&&c.boundary!=main.rows-1) throw std::runtime_error("Branch seam requires an outer main boundary.");
    for(size_t i=1;i<c.seam.size();++i) if(c.seam[i]!=c.seam[i-1]+1)
        throw std::runtime_error("Branch material seam must be a contiguous ordered interval.");
    if(c.seam.front()<=0||c.seam.back()>=main.columns-1) throw std::runtime_error("Branch roots must remain interior along the main boundary.");
}
std::vector<Connection> connections(const std::vector<MaterialGrid>& grids,const double* parameters) {
    std::vector<Connection> result;
    for(size_t i=1;i<grids.size();++i) {
        auto current=connection(grids[0],grids[i],parameters+2*i); validate(current,grids[0]);
        for(const auto& previous:result)
            if(current.boundary==previous.boundary&&current.seam.front()<=previous.seam.back()&&current.seam.back()>=previous.seam.front())
                throw std::runtime_error("Branch intervals cannot overlap or share endpoints.");
        result.push_back(std::move(current));
    }
    return result;
}
void share_displacements(const Mesh& source,const std::vector<MaterialGrid>& grids,const std::vector<Connection>& seams,std::vector<Points>& values) {
    for(size_t b=1;b<grids.size();++b) for(size_t i=0;i<seams[b-1].seam.size();++i) {
        const auto& grid=grids[b]; const int a=seams[b-1].boundary*grids[0].columns+seams[b-1].seam[i];
        const auto j=i*size_t(grid.columns); const V3 base=source.vertices.row(grid.indices[j]);
        V3 value=base;
        if(i&&i+1<seams[b-1].seam.size()) value+=(values[0][size_t(a)]+values[b][j]-2*base)*.5;
        values[0][size_t(a)]=values[b][j]=value;
    }
}
}
