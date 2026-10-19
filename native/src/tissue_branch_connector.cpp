// SPDX-License-Identifier: GPL-3.0-or-later
// Port of branch_connector.py: local Hermite strip, physical rail spacing and fullness.
#include "tissue_branches.hpp"

namespace af::tissue {
struct View {
    const Points& points; int rows,cols; bool reverse=false;
    V3 at(int i,int j) const { return points[size_t((reverse?rows-1-i:i)*cols+j)]; }
};
struct Strip { Points points; std::vector<double> t; V3 incoming,outgoing; };
static V3 safe_unit(const V3& value) { return value/std::max(value.norm(),1e-12); }
static double smooth(double x) { x=std::clamp(x,0.,1.); return x*x*(3-2*x); }
static int main_rail(const View& main,const Connection& c) {
    std::vector<double> lengths(size_t(main.rows),0);
    for(int i=1;i<main.rows;++i) {
        double distance=0; for(int j:c.seam) distance+=(main.at(i,j)-main.at(i-1,j)).norm();
        lengths[size_t(i)]=lengths[size_t(i-1)]+distance/double(c.seam.size());
    }
    const double total=std::max(lengths.back(),1e-12);
    for(double& value:lengths) value/=total;
    return std::clamp(int(std::lower_bound(lengths.begin(),lengths.end(),1-c.width)-lengths.begin()),1,main.rows-2);
}
static V3 fullness_normal(const View& main,const View& child,const Connection& c,int i,int k,int row,bool flip) {
    const int before=std::max(0,row-1),after=std::min(child.rows-1,row+1),j=c.seam[size_t(row)];
    const V3 main_gradient=main.at(i,c.seam[size_t(after)])-main.at(i,c.seam[size_t(before)]);
    const V3 branch_gradient=child.at(after,k)-child.at(before,k);
    const V3 first=safe_unit((main.at(i,j)-main.at(i-1,j)).cross(main_gradient));
    const V3 second=safe_unit((child.at(row,k+1)-child.at(row,k)).cross(branch_gradient));
    const V3 normal=(first+second).norm()>1e-10?safe_unit(first+second):first;
    return flip?-normal:normal;
}
static Strip strip(const View& main,const View& child,const Connection& c,int rail,int k,int row) {
    Strip result; const int column=c.seam[size_t(row)];
    for(int i=rail;i<main.rows;++i) result.points.push_back(main.at(i,column));
    for(int j=1;j<=k;++j) result.points.push_back(child.at(row,j));
    result.t.resize(result.points.size(),0);
    for(size_t j=1;j<result.t.size();++j) result.t[j]=result.t[j-1]+(result.points[j]-result.points[j-1]).norm();
    const double length=result.t.back();
    result.incoming=safe_unit(result.points.front()-main.at(rail-1,column))*length;
    result.outgoing=safe_unit(child.at(row,k+1)-result.points.back())*length;
    for(double& value:result.t) value/=std::max(length,1e-12);
    return result;
}
static Points hermite(const Strip& strip,const V3& normal,double fullness,double weight) {
    Points result; const auto& first=strip.points.front(); const auto& last=strip.points.back();
    for(size_t j=0;j<strip.points.size();++j) {
        const double t=strip.t[j],t2=t*t,t3=t2*t;
        const V3 target=(2*t3-3*t2+1)*first+(t3-2*t2+t)*strip.incoming+(-2*t3+3*t2)*last+(t3-t2)*strip.outgoing;
        const V3 filled=target+normal*(16*t2*(1-t)*(1-t)*fullness);
        result.push_back((1-weight)*strip.points[j]+weight*filled);
    }
    return result;
}
static std::vector<Points> replacement(const View& main,const View& child,const Connection& c,int rail,int k,bool flip,uint64_t cancel) {
    std::vector<Points> result;
    for(int row=0;row<child.rows;++row) {
        check_cancel(cancel); const auto geometry=strip(main,child,c,rail,k,row);
        const auto normal=fullness_normal(main,child,c,rail,k,row,flip);
        const double across=c.across[size_t(row)],weight=smooth(std::min(across,1-across)/.1);
        result.push_back(hermite(geometry,normal,c.fullness,weight));
    }
    return result;
}
static void install(Points& main,Points& branch,const MaterialGrid& grid,const MaterialGrid& child,const Connection& c,const std::vector<Points>& rows,int rail,int k) {
    const int count=grid.rows-rail;
    for(size_t row=0;row<rows.size();++row) {
        for(int i=rail;i<grid.rows;++i) {
            const int index=(c.boundary==0?grid.rows-1-i:i)*grid.columns+c.seam[row];
            main[size_t(index)]=rows[row][size_t(i-rail)];
        }
        for(int j=0;j<=k;++j) branch[row*size_t(child.columns)+j]=rows[row][size_t(count-1+j)];
    }
}
void connect_parts(const std::vector<MaterialGrid>& grids,const std::vector<Connection>& seams,std::vector<Points>& values,bool flip,uint64_t cancel) {
    for(size_t b=1;b<grids.size();++b) {
        const auto& c=seams[b-1]; const auto& grid=grids[b];
        const View main{values[0],grids[0].rows,grids[0].columns,c.boundary==0},child{values[b],grid.rows,grid.columns};
        const int rail=main_rail(main,c),k=std::clamp(int(std::lower_bound(c.along.begin(),c.along.end(),c.width)-c.along.begin()),1,grid.columns-2);
        const auto rows=replacement(main,child,c,rail,k,flip!=(c.boundary==0),cancel);
        install(values[0],values[b],grids[0],grid,c,rows,rail,k);
    }
}
}
