#include "anthroforge/skin_fit.h"
#include "skin_fit_validation.hpp"
#include <Eigen/Geometry>

namespace af::skin::fit {
static Transform basis(const Vertices& points,const Eigen::VectorXd& weights) {
    Transform result=Transform::Identity();
    result.topLeftCorner<3,3>()<<1,0,0, 0,0,-1, 0,1,0;
    result.topRightCorner<3,1>()=points.transpose()*weights/std::max(weights.sum(),1e-12);
    return result;
}
static void channels(const Transform& matrix,double* output,const double* previous) {
    Eigen::Vector3d scale=matrix.topLeftCorner<3,3>().colwise().norm();
    Eigen::Quaterniond rotation(matrix.topLeftCorner<3,3>()*scale.cwiseInverse().asDiagonal());
    rotation.normalize(); Eigen::Map<Eigen::Vector3d> position(output); position=matrix.topRightCorner<3,1>();
    Eigen::Vector4d q(rotation.w(),rotation.x(),rotation.y(),rotation.z());
    if(previous&&q.dot(Eigen::Map<const Eigen::Vector4d>(previous+3))<0) q=-q;
    Eigen::Map<Eigen::Vector4d>(output+3)=q; Eigen::Map<Eigen::Vector3d>(output+7)=scale;
}
static Transform local(const double* left,const double* right,double t) {
    Eigen::Matrix<double,10,1> value=(1-t)*Eigen::Map<const Eigen::Matrix<double,10,1>>(left)+
        t*Eigen::Map<const Eigen::Matrix<double,10,1>>(right);
    Eigen::Quaterniond rotation(value(3),value(4),value(5),value(6));
    if(rotation.norm()<1e-12||!value.allFinite()) throw std::runtime_error("Invalid fitted playback channels.");
    Transform result=Transform::Identity();
    result.topLeftCorner<3,3>()=rotation.normalized().toRotationMatrix()*value.tail<3>().asDiagonal();
    result.topRightCorner<3,1>()=value.head<3>(); return result;
}
static std::pair<int,double> interval(const double* keys,int frames,double value) {
    if(!std::isfinite(value)) throw std::runtime_error("Fitted playback value must be finite.");
    for(int i=0;i<frames;++i) if(!std::isfinite(keys[i])||(i&&keys[i]<=keys[i-1]))
        throw std::runtime_error("Fitted sample keys must be increasing.");
    value=std::clamp(value,keys[0],keys[frames-1]);
    int right=std::min(int(std::upper_bound(keys,keys+frames,value)-keys),frames-1),left=std::max(0,right-1);
    return {left,(value-keys[left])/(keys[right]-keys[left])};
}
static void capture(const double* points,int count,const double* weights,int bones,const double* matrices,
    int frames,double* bases,double* values,uint64_t cancel) {
    validate_prediction(points,count,weights,bones,matrices,frames);
    Eigen::Map<const Vertices> rest(points,count,3); Eigen::Map<const Dense> w(weights,count,bones);
    for(int j=0;j<bones;++j) {
        check_cancel(cancel); Transform b=basis(rest,w.col(j)),inverse=b.inverse(); Eigen::Map<Transform>(bases+16*j)=b;
        for(int k=0;k<frames;++k) {
            const double* previous=k?values+int64_t((k-1)*bones+j)*10:nullptr;
            channels(inverse*Eigen::Map<const Transform>(matrices+int64_t(k*bones+j)*16)*b,
                values+int64_t(k*bones+j)*10,previous);
        }
    }
}
static void playback(const double* points,int count,const double* weights,int bones,const double* bases,
    const double* keys,const double* channels,int frames,double value,double* output,uint64_t cancel) {
    validate_weights(weights,count,bones); auto [left,t]=interval(keys,frames,value);
    Eigen::Map<const Vertices> rest(points,count,3); Eigen::Map<Vertices> result(output,count,3); result.setZero();
    Eigen::Map<const Dense> w(weights,count,bones);
    for(int j=0;j<bones;++j) {
        check_cancel(cancel); Transform b=Eigen::Map<const Transform>(bases+16*j);
        Transform m=b*local(channels+int64_t(left*bones+j)*10,channels+int64_t((left+1)*bones+j)*10,t)*b.inverse();
        for(int i=0;i<count;++i) result.row(i)+=w(i,j)*(m.topLeftCorner<3,3>()*rest.row(i).transpose()+m.topRightCorner<3,1>()).transpose();
    }
    if(!result.allFinite()) throw std::runtime_error("Nonfinite fitted playback.");
}
}
int af_skin_fit_channels(const double* vertices,int count,const double* weights,int bones,const double* matrices,
    int frames,double* bases,double* channels,uint64_t cancel) {
    try {
        if(!vertices||!weights||!matrices||!bases||!channels) throw std::runtime_error("Missing fitted channels inputs.");
        af::skin::fit::capture(vertices,count,weights,bones,matrices,frames,bases,channels,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_skin_fit_playback(const double* vertices,int count,const double* weights,int bones,const double* bases,
    const double* keys,const double* channels,int frames,double value,double* output,uint64_t cancel) {
    try {
        if(!vertices||!weights||!bases||!keys||!channels||!output||count<1||bones<1||frames<2)
            throw std::runtime_error("Invalid fitted playback inputs.");
        af::skin::fit::playback(vertices,count,weights,bones,bases,keys,channels,frames,value,output,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
