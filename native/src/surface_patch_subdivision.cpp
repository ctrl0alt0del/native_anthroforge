// SPDX-License-Identifier: GPL-3.0-or-later
// Shared edge identities and triangle subdivision from addon fiber_surface.py.
#include "surface_patch_internal.hpp"

namespace af::curve_surface {
static PatchKey key(const Triangle& triangle,int index,const Triangle& weights,int level) {
    for(int i=0;i<3;++i) if(weights[i]==level) return {0,triangle[i],0,0,0};
    for(int i=0;i<3;++i) if(weights[i]==0) {
        const int a=(i+1)%3,b=(i+2)%3,low=std::min(triangle[a],triangle[b]),high=std::max(triangle[a],triangle[b]);
        return {1,low,high,weights[triangle[a]==high?a:b],0};
    }
    return {2,index,weights[0],weights[1],weights[2]};
}
static int vertex(Patch& patch,const Points& source,const Triangle& t,int index,const Triangle& w,int level) {
    const auto identity=key(t,index,w,level); const auto found=patch.indices.find(identity);
    if(found!=patch.indices.end()) return found->second;
    const int added=int(patch.points.size()); patch.indices.emplace(identity,added); patch.keys.push_back(identity);
    patch.points.push_back((source[t[0]]*w[0]+source[t[1]]*w[1]+source[t[2]]*w[2])/double(level));
    return added;
}
static void faces(Patch& patch,const std::vector<std::vector<int>>& grid,int level) {
    for(int i=0;i<level;++i)
        for(int j=0;j<level-i;++j) {
            patch.faces.push_back({grid[i][j],grid[i+1][j],grid[i][j+1]});
            if(j<level-i-1) patch.faces.push_back({grid[i+1][j],grid[i+1][j+1],grid[i][j+1]});
        }
}
static void triangle(Patch& patch,const Points& source,const Triangle& t,int index,int level,uint64_t cancel) {
    std::vector<std::vector<int>> grid(size_t(level+1),std::vector<int>(size_t(level+1)));
    for(int i=0;i<=level;++i) {
        check_cancel(cancel);
        for(int j=0;j<=level-i;++j) grid[i][j]=vertex(patch,source,t,index,{i,j,level-i-j},level);
    }
    faces(patch,grid,level);
}
Patch subdivide(const Points& points,const std::vector<Triangle>& triangles,int level,uint64_t cancel) {
    budget(triangles.size()*size_t(level+1)*size_t(level+2),2*triangles.size()*size_t(level)*size_t(level));
    Patch result;
    for(size_t i=0;i<triangles.size();++i) triangle(result,points,triangles[i],int(i),level,cancel);
    return result;
}
}
