// SPDX-License-Identifier: GPL-3.0-or-later
// Qualified addon Section Profile formula with scale-aware degenerate-frame handling.
#include "construction_internal.hpp"
#include "tissue_profile.hpp"
#include "tissue_kernel.hpp"

namespace af::tissue {
using kernel::Vec;
static std::vector<Vec> stable_frames(const std::vector<Vec>& base,int rows,int columns,
    double limit,std::vector<double>& areas) {
    std::vector<Vec> normals(base.size()); areas.resize(base.size());
    for(int i=0;i<rows;++i) for(int j=0;j<columns;++j) {
        const int k=i*columns+j;
        const Vec value=kernel::cross(kernel::af_env_gradient(base,rows,columns,i,j,0),
            kernel::af_env_gradient(base,rows,columns,i,j,1));
        areas[k]=kernel::norm(value);
        normals[k]=areas[k]>limit?kernel::af_env_unit(value):Vec{0,0,0};
        const int previous=j?k-1:(i?(i-1)*columns:-1);
        if(previous>=0&&kernel::dot(normals[k],normals[previous])<0) normals[k]=kernel::mul(normals[k],-1);
    }
    return normals;
}
static double profile_height(const double* settings,int i,int j,int rows,int columns) {
    const double depth[6]={0,settings[0],settings[1],settings[2],settings[3],0};
    const double peak[6]={settings[4],settings[4],settings[5],settings[6],settings[7],settings[7]};
    const double u=double(j)/(columns-1),v=double(i)/(rows-1);
    const double d=std::max(0.,kernel::af_env_pchip(depth,u)),q=kernel::af_env_pchip(peak,u);
    const double x=v<=q?v/q:(1-v)/(1-q);
    return d*std::pow(std::max(0.,x*(2-x)),settings[8]);
}
std::vector<Vec> section_directions(const std::vector<Vec>& base,int rows,int columns,
    int mode,std::vector<double>& areas) {
    const double limit=1e-12*std::pow(kernel::af_env_diagonal(base),2);
    auto normals=stable_frames(base,rows,columns,limit,areas);
    return kernel::af_env_directions(std::move(normals),areas,rows,columns,mode);
}
int section_profile(const std::vector<Vec>& base,int rows,int columns,const double* settings,
    int mode,int sign,std::vector<Vec>& output) {
    const double limit=1e-12*std::pow(kernel::af_env_diagonal(base),2);
    std::vector<double> areas;
    auto normals=section_directions(base,rows,columns,mode,areas); output=base;
    for(int i=1;i<rows-1;++i) for(int j=1;j<columns-1;++j) {
        const int k=i*columns+j; const double height=profile_height(settings,i,j,rows,columns);
        if(height==0) continue;
        if(areas[k]<=limit||kernel::norm(normals[k])<=1e-12) return 2;
        output[k]=kernel::add(base[k],kernel::mul(kernel::af_env_unit(normals[k]),sign*height));
    }
    return 0;
}
}
