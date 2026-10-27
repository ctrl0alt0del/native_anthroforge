#include "skin_contact_kernel.hpp"
#include "anthroforge/skin_contact.h"
namespace af::skin::contact {
static void validate(const AfSkinContact& a) {
    if(!a.reference||!a.current||!a.proposed||!a.faces||!a.symmetry||!a.plane||a.count<3||a.face_count<1)
        throw std::runtime_error("Missing skin contact inputs.");
    if(uint64_t(a.count)*128+uint64_t(a.face_count)*128>a.budget) throw std::runtime_error("CONTACT_MEMORY_LIMIT");
}
static void initialize(af_ad::ContactTask& s,const AfSkinContact& a,uint64_t cancel) {
    validate(a); s.reference=Eigen::Map<const af_ad::RM>(a.reference,a.count,3); s.start=s.reference;
    s.x=Eigen::Map<const af_ad::RM>(a.proposed,a.count,3); s.faces=Eigen::Map<const af_ad::RI>(a.faces,a.face_count,3);
    s.symmetry=Eigen::Map<const Eigen::VectorXi>(a.symmetry,a.count); s.origin=V3(a.plane); s.normal=V3(a.plane+3);
    s.budget=a.budget; s.token=cancel;
    const double scale=(s.reference.colwise().maxCoeff()-s.reference.colwise().minCoeff()).norm();
    s.tolerance=std::max(scale*1e-9,1e-12); s.reach=10*s.tolerance;
    if(!s.reference.allFinite()||!s.x.allFinite()||!s.origin.allFinite()||!s.normal.allFinite())
        throw std::runtime_error("Nonfinite skin contact positions or plane.");
    if(s.faces.minCoeff()<0||s.faces.maxCoeff()>=a.count||s.symmetry.minCoeff()<-1||s.symmetry.maxCoeff()>=a.count)
        throw std::runtime_error("Invalid skin contact topology or symmetry addresses.");
}
static void evaluate(const AfSkinContact& input,double* output,double* report,uint64_t cancel) {
    if(!output||!report) throw std::runtime_error("Missing skin contact output buffers.");
    check_cancel(cancel); af_ad::ContactTask task; initialize(task,input,cancel);
    const af_ad::M published=Eigen::Map<const af_ad::RM>(input.current,input.count,3);
    if(!published.allFinite()) throw std::runtime_error("Nonfinite accepted skin positions.");
    af_ad::contact_solve(task,report); af_ad::validate_published_motion(task,published,report);
    check_cancel(cancel);
    if(!task.x.allFinite()) throw std::runtime_error("Nonfinite skin contact result.");
    Eigen::Map<af_ad::RM>(output,input.count,3)=task.x;
}
}
int af_skin_contact(const AfSkinContact* input,double* output,double* report,uint64_t cancel) {
    try {
        if(!input) throw std::runtime_error("Missing skin contact input.");
        af::skin::contact::evaluate(*input,output,report,cancel); return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
int af_skin_contact_symmetry(const double* points,int count,const double* plane,int* partners,double* maximum,uint64_t cancel) {
    try {
        if(!points||!plane||!partners||!maximum||count<1) throw std::runtime_error("Missing symmetry input.");
        const Eigen::Map<const af::Vertices> vertices(points,count,3);
        if(!vertices.allFinite()||!af::V3(plane).allFinite()||!af::V3(plane+3).allFinite()) throw std::runtime_error("Nonfinite symmetry input.");
        af::check_cancel(cancel);
        if(!af_ad::af_ad_symmetry(points,count,plane,partners,maximum)) throw std::runtime_error(af_ad::error);
        af::check_cancel(cancel); return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
