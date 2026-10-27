#include "skin_deformation.hpp"
#include <set>
namespace af::skin::deformation {
static std::vector<double> areas(const double* xyz,int n,const int* faces,int nf,int arity,uint64_t cancel) {
    const Eigen::Map<const Vertices> points(xyz,n,3); std::vector<double> mass(n,0);
    if(!points.allFinite()) throw std::runtime_error("Anatomical sample positions must be finite.");
    for(int f=0;f<nf;++f) {
        check_cancel(cancel);
        for(int k=0;k<arity;++k) if(faces[f*arity+k]<0||faces[f*arity+k]>=n) throw std::runtime_error("Invalid anatomical face index.");
        for(int k=1;k<arity-1;++k) {
            const int a=faces[f*arity],b=faces[f*arity+k],c=faces[f*arity+k+1];
            const V3 u=points.row(b)-points.row(a),v=points.row(c)-points.row(a); const double area=u.cross(v).norm()/6;
            mass[a]+=area; mass[b]+=area; mass[c]+=area;
        }
    }
    return mass;
}
static int select(const std::vector<double>& mass,int* out,double* total) {
    std::vector<int> keep; std::vector<double> cumulative; *total=0;
    for(int i=0;i<int(mass.size());++i) if(mass[i]>0) { keep.push_back(i); *total+=mass[i]; cumulative.push_back(*total); }
    if(keep.empty()||!std::isfinite(*total)) throw std::runtime_error("Contributor has no nondegenerate material surface.");
    const int count=std::min(80,int(keep.size())); std::set<int> selected;
    for(int i=0;i<count;++i) {
        const double target=(i+.5)*(*total)/count;
        const size_t address=std::lower_bound(cumulative.begin(),cumulative.end(),target)-cumulative.begin();
        selected.insert(keep.at(address));
    }
    std::copy(selected.begin(),selected.end(),out); return int(selected.size());
}
}
int af_skin_deformation_samples(const double* points,int count,const int* faces,int face_count,int arity,int* selected,double* mass,uint64_t cancel) {
    try {
        if(!points||!faces||!selected||!mass||count<3||face_count<1||arity<3) throw std::runtime_error("Missing anatomical sample inputs.");
        return af::skin::deformation::select(af::skin::deformation::areas(points,count,faces,face_count,arity,cancel),selected,mass);
    } catch(const std::exception& e) { af::set_error(e.what()); return -1; }
}
