#pragma once
#include <DemBones/DemBones.h>
#include <chrono>
#include <stdexcept>
#include <string>
#include <omp.h>
#include <Eigen/Geometry>
#include <Eigen/SVD>
#include <set>
namespace af::skin::fit::donor {
using M=Eigen::MatrixXd;
using V=Eigen::Vector3d;
using R4=Eigen::Matrix<double,4,4,Eigen::RowMajor>;
using R=Eigen::Matrix<double,Eigen::Dynamic,Eigen::Dynamic,Eigen::RowMajor>;
static thread_local std::string error;
#define API static
static thread_local uint64_t cancellation=0;
struct Solver:Dem::DemBones<double,double> {
    std::chrono::steady_clock::time_point start=std::chrono::steady_clock::now();
    void deadline() {af::check_cancel(cancellation);}
    bool cbIterEnd() override {deadline(); return false;}
    void cbInitSplitEnd() override {deadline();}
};

static void setup(Solver& s,const double* rest,int n,const int* faces,int q,const double* targets,int f,int b) {
    s.nV=n; s.nB=b; s.nS=1; s.nF=f; s.nnz=std::min(4,b); s.nIters=40;
    s.fStart.resize(2); s.fStart<<0,f; s.subjectID=Eigen::VectorXi::Zero(f);
    s.u=Eigen::Map<const Eigen::Matrix<double,3,Eigen::Dynamic>>(rest,3,n);
    s.v.resize(3*f,n);
    for(int k=0;k<f;++k) s.v.middleRows(3*k,3)=Eigen::Map<const Eigen::Matrix<double,3,Eigen::Dynamic>>(targets+3*n*k,3,n);
    s.fv.resize(q);
    for(int i=0;i<q;++i) s.fv[i]=std::vector<int>(faces+4*i,faces+4*i+4);
}

static void output(const Solver& s,int capacity,double* weights,double* matrices) {
    Eigen::Map<R> w(weights,s.nV,capacity); w.setZero();
    w.leftCols(s.nB)=M(s.w).transpose();
    for(int k=0;k<s.nF;++k) for(int j=0;j<s.nB;++j)
        Eigen::Map<R4>(matrices+16*(k*capacity+j))=s.m.block(4*k,4*j,4,4);
}

API const char* db_error() {return error.c_str();}
API int db_fit(const double* rest,int n,const int* faces,int q,const double* targets,int f,int b,double* weights,double* matrices) {
    try {omp_set_num_threads(4); Solver s; setup(s,rest,n,faces,q,targets,f,b); s.compute(); output(s,b,weights,matrices); return s.nB;}
    catch(const std::exception& e) {error=e.what(); return 0;}
}

API int db_oracle(const double* rest,int n,const int* faces,int q,const double* targets,int f,int b,const double* weights,double* matrices) {
    try {Solver s; setup(s,rest,n,faces,q,targets,f,b); s.nTransIters=100;
        s.w=Eigen::Map<const R>(weights,n,b).transpose().sparseView(); s.computeTranformations();
        for(int k=0;k<f;++k) for(int j=0;j<b;++j) Eigen::Map<R4>(matrices+16*(k*b+j))=s.m.block(4*k,4*j,4,4);
        return 1;
    } catch(const std::exception& e) {error=e.what(); return 0;}
}

API void db_interpolate(const double* left,const double* right,int b,double t,double* output) {
    for(int j=0;j<b;++j) {
        R4 a=Eigen::Map<const R4>(left+16*j),c=Eigen::Map<const R4>(right+16*j),m=R4::Identity();
        Eigen::Quaterniond qa(a.topLeftCorner<3,3>()),qc(c.topLeftCorner<3,3>());
        m.topLeftCorner<3,3>()=qa.slerp(t,qc).normalized().toRotationMatrix();
        m.topRightCorner<3,1>()=(1-t)*a.topRightCorner<3,1>()+t*c.topRightCorner<3,1>();
        Eigen::Map<R4>(output+16*j)=m;
    }
}

API void db_skin(const double* rest,int n,const double* weights,int b,const double* matrices,double* output) {
    for(int i=0;i<n;++i) {
        V p=Eigen::Map<const V>(rest+3*i),v=V::Zero();
        for(int j=0;j<b;++j) if(weights[i*b+j]>0) {
            Eigen::Map<const R4> m(matrices+16*j);
            v+=weights[i*b+j]*(m.topLeftCorner<3,3>()*p+m.topRightCorner<3,1>());
        }
        Eigen::Map<V>(output+3*i)=v;
    }
}
using M3=Eigen::Matrix3d;
struct Moment {double mass=0; V x=V::Zero(),y=V::Zero(); M3 xx=M3::Zero(),yx=M3::Zero();};
static M3 rotation(const M3& c) {
    Eigen::JacobiSVD<M3> svd(c,Eigen::ComputeFullU|Eigen::ComputeFullV);
    M3 d=M3::Identity(); d(2,2)=(svd.matrixU()*svd.matrixV().transpose()).determinant();
    return svd.matrixU()*d*svd.matrixV().transpose();
}
static Moment moments(const M& x,const M& residual,const Eigen::VectorXd& w) {
    Moment a;
    for(int i=0;i<x.cols();++i) if(w(i)>0) {
        double z=w(i)*w(i); a.mass+=z; a.x+=z*x.col(i); a.y+=w(i)*residual.col(i);
        a.xx+=z*x.col(i)*x.col(i).transpose(); a.yx+=w(i)*residual.col(i)*x.col(i).transpose();
    }
    if(a.mass>1e-20) {a.x/=a.mass; a.y/=a.mass; a.xx-=a.mass*a.x*a.x.transpose(); a.yx-=a.mass*a.y*a.x.transpose();}
    return a;
}
static M3 scaled_rotation(const Moment& a,int mode) {
    V scale=V::Ones(); M3 r=rotation(a.yx);
    for(int k=0;k<40;++k) {
        r=rotation(a.yx*scale.asDiagonal()); V d=(r.transpose()*a.yx).diagonal();
        if(mode==1) scale.setConstant(d.sum()/std::max(1e-20,a.xx.trace()));
        if(mode==2) for(int j=0;j<3;++j) scale(j)=d(j)/std::max(1e-20,a.xx(j,j));
        scale=scale.cwiseMax(.25).cwiseMin(4.);
    }
    return r*scale.asDiagonal();
}
static M contribution(const M& x,const R4& t,const Eigen::VectorXd& w) {
    M y=t.topLeftCorner<3,3>()*x; y.colwise()+=t.topRightCorner<3,1>();
    return y*w.asDiagonal();
}
static void frame(Solver& s,int k,int mode) {
    M residual=s.v.middleRows(3*k,3); M weights=M(s.w); M x=s.u;
    for(int j=0;j<s.nB;++j) residual-=contribution(x,s.m.block(4*k,4*j,4,4),weights.row(j).transpose());
    for(int pass=0;pass<3;++pass) for(int j=0;j<s.nB;++j) {
        Eigen::VectorXd w=weights.row(j).transpose(); R4 t=s.m.block(4*k,4*j,4,4);
        residual+=contribution(x,t,w); Moment a=moments(x,residual,w);
        if(a.mass>1e-20) {t.topLeftCorner<3,3>()=scaled_rotation(a,mode); t.topRightCorner<3,1>()=a.y-t.topLeftCorner<3,3>()*a.x;}
        s.m.block(4*k,4*j,4,4)=t; residual-=contribution(x,t,w);
    }
}
API int sb_fit(const double* rest,int n,const int* faces,int q,const double* targets,int f,int b,int mode,double* weights,double* matrices) {
    try {omp_set_num_threads(4); Solver s; setup(s,rest,n,faces,q,targets,f,b); s.compute();
        for(int iteration=0;iteration<40;++iteration) {
            if(mode==0) s.computeTranformations();
            else {
                #pragma omp parallel for
                for(int k=1;k<f;++k) frame(s,k,mode);
            }
            s.computeWeights(); s.deadline();
        }
        output(s,b,weights,matrices); return s.nB;
    } catch(const std::exception& e) {error=e.what(); return 0;}
}
API void sb_interpolate(const double* left,const double* right,int b,double t,double* output) {
    for(int j=0;j<b;++j) {
        R4 a=Eigen::Map<const R4>(left+16*j),c=Eigen::Map<const R4>(right+16*j),m=R4::Identity();
        V sa=a.topLeftCorner<3,3>().colwise().norm(),sc=c.topLeftCorner<3,3>().colwise().norm();
        Eigen::Quaterniond qa(a.topLeftCorner<3,3>()*sa.cwiseInverse().asDiagonal()),qc(c.topLeftCorner<3,3>()*sc.cwiseInverse().asDiagonal());
        m.topLeftCorner<3,3>()=qa.slerp(t,qc).normalized().toRotationMatrix()*((1-t)*sa+t*sc).asDiagonal();
        m.topRightCorner<3,1>()=(1-t)*a.topRightCorner<3,1>()+t*c.topRightCorner<3,1>();
        Eigen::Map<R4>(output+16*j)=m;
    }
}
using Edges=std::vector<std::vector<int>>;
static Edges adjacency(const int* faces,int q,int n) {
    std::vector<std::set<int>> sets(n); Edges result(n);
    for(int f=0;f<q;++f) for(int j=0;j<4;++j) {int a=faces[4*f+j],b=faces[4*f+(j+1)%4]; sets[a].insert(b); sets[b].insert(a);}
    for(int i=0;i<n;++i) result[i]=std::vector<int>(sets[i].begin(),sets[i].end());
    return result;
}
static R4 single_transform(const M& x,const M& target,const Eigen::VectorXd& w,bool affine) {
    M residual=target-x*(Eigen::VectorXd::Ones(w.size())-w).asDiagonal(); Moment a=moments(x,residual,w); R4 t=R4::Identity();
    if(a.mass<1e-20) return t;
    if(affine) {double ridge=std::max(1e-12,a.xx.trace()*1e-10); t.topLeftCorner<3,3>()=(a.xx+ridge*M3::Identity()).ldlt().solve((a.yx+ridge*M3::Identity()).transpose()).transpose();}
    else t.topLeftCorner<3,3>()=scaled_rotation(a,2);
    t.topRightCorner<3,1>()=a.y-t.topLeftCorner<3,3>()*a.x; return t;
}
static void single_weights(const M& x,const std::vector<M>& targets,const std::vector<R4>& ts,Eigen::VectorXd& w,const Edges& edges,double lambda,bool hard) {
    Eigen::VectorXd num=Eigen::VectorXd::Zero(w.size()),den=num;
    for(int k=1;k<targets.size();++k) {M delta=contribution(x,ts[k],Eigen::VectorXd::Ones(w.size()))-x; M y=targets[k]-x;
        for(int i=0;i<w.size();++i) {num(i)+=delta.col(i).dot(y.col(i)); den(i)+=delta.col(i).squaredNorm();}}
    for(int sweep=0;sweep<(lambda>0?40:1);++sweep) for(int i=0;i<w.size();++i) {
        if(hard) {w(i)=2*num(i)>den(i)?1.:0.; continue;}
        double sum=0; for(int j:edges[i]) sum+=w(j);
        w(i)=std::clamp((num(i)+lambda*sum)/std::max(1e-20,den(i)+lambda*edges[i].size()),0.,1.);
    }
}
static double single_loss(const M& x,const std::vector<M>& targets,const std::vector<R4>& ts,const Eigen::VectorXd& w,const Edges& edges,double lambda) {
    double loss=0;
    for(int k=1;k<targets.size();++k) loss+=(contribution(x,ts[k],w)+x*(Eigen::VectorXd::Ones(w.size())-w).asDiagonal()-targets[k]).squaredNorm();
    for(int i=0;i<w.size();++i) for(int j:edges[i]) if(j>i) loss+=lambda*std::pow(w(i)-w(j),2);
    return loss;
}
static void single_trial(const M& x,const std::vector<M>& targets,const Edges& edges,bool affine,bool hard,double lambda,int seed,Eigen::VectorXd& w,std::vector<R4>& ts,double& loss) {
    w=Eigen::VectorXd::Zero(x.cols());
    for(int k=1;k<targets.size();++k) for(int i=0;i<x.cols();++i) w(i)=std::max(w(i),(targets[k].col(i)-x.col(i)).norm());
    double maximum=w.maxCoeff(); w/=std::max(1e-20,maximum);
    if(seed==0) w.setOnes(); if(seed==2) w=(w.array()>.1).cast<double>(); if(hard) w=(w.array()>.1).cast<double>();
    ts.assign(targets.size(),R4::Identity()); double previous=1e100;
    for(int it=0;it<200;++it) {
        af::check_cancel(cancellation);
        for(int k=1;k<targets.size();++k) ts[k]=single_transform(x,targets[k],w,affine);
        single_weights(x,targets,ts,w,edges,lambda,hard); loss=single_loss(x,targets,ts,w,edges,lambda);
        if(it>20 && abs(previous-loss)<1e-9*std::max(1.,previous)) break; previous=loss;
    }
    for(int k=1;k<targets.size();++k) ts[k]=single_transform(x,targets[k],w,affine);
    loss=single_loss(x,targets,ts,w,edges,lambda);
}
API int one_fit(const double* rest,int n,const int* faces,int q,const double* values,int f,int affine,int hard,double smooth,double* weights,double* matrices,double* stats) {
    try {M x=Eigen::Map<const Eigen::Matrix<double,3,Eigen::Dynamic>>(rest,3,n); std::vector<M> targets; auto edges=adjacency(faces,q,n); double energy=0,best=1e100;
        for(int k=0;k<f;++k) {targets.push_back(Eigen::Map<const Eigen::Matrix<double,3,Eigen::Dynamic>>(values+3*n*k,3,n)); energy+=(targets.back()-x).squaredNorm();}
        double lambda=smooth*energy/n; stats[0]=lambda;
        for(int seed=0;seed<3;++seed) {Eigen::VectorXd w; std::vector<R4> ts; double loss; single_trial(x,targets,edges,affine,hard,lambda,seed,w,ts,loss); stats[2+seed]=loss;
            if(loss<best) {best=loss; stats[1]=seed; for(int i=0;i<n;++i) {weights[2*i]=1-w(i); weights[2*i+1]=w(i);}
                for(int k=0;k<f;++k) {Eigen::Map<R4>(matrices+32*k)=R4::Identity(); Eigen::Map<R4>(matrices+32*k+16)=ts[k];}}}
        return 1;
    } catch(const std::exception& e) {error=e.what(); return 0;}
}
#undef API
}
