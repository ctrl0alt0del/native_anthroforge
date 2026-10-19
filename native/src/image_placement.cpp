#include "mesh_internal.hpp"
#include "anthroforge/image.h"

namespace af {
static bool image_hit(const M4& frame,const double* size,int side,const V3& origin,const V3& direction,double* hit) {
    const M4 inverse=frame.inverse();
    const V3 p=(inverse*origin.homogeneous()).head<3>(), d=inverse.block<3,3>(0,0)*direction;
    if(!frame.allFinite()||std::abs(d.z())<1e-14) return false;
    const bool front=frame.block<3,3>(0,0).determinant()*d.z()<0;
    if((side==1&&!front)||(side==2&&front)) return false;
    const double distance=-p.z()/d.z(); const V3 local=p+distance*d;
    const double u=local.x()/size[0]+.5, v=.5-local.y()/size[1];
    if(!std::isfinite(distance)||distance<0||u<0||u>1||v<0||v>1) return false;
    hit[1]=distance; hit[2]=u; hit[3]=v;
    Eigen::Map<V3>(hit+4)=origin+distance*direction; hit[7]=front?1:0; return true;
}
static void image_vertex(float* output,double x,double y,float u,float v) {
    output[0]=float(x); output[1]=float(y); output[2]=0;
    output[3]=0; output[4]=0; output[5]=1; output[6]=u; output[7]=v;
}
static void image_quad(const int* info,const uint64_t* size,double width,double height,float* output) {
    const double left=(double(info[0])/size[0]-.5)*width, right=(double(info[0]+info[2])/size[0]-.5)*width;
    const double top=(.5-double(info[1])/size[1])*height, bottom=(.5-double(info[1]+info[3])/size[1])*height;
    image_vertex(output,left,bottom,0,1); image_vertex(output+8,right,bottom,1,1);
    image_vertex(output+16,right,top,1,0); image_vertex(output+24,left,bottom,0,1);
    image_vertex(output+32,right,top,1,0); image_vertex(output+40,left,top,0,0);
}
}
// Blender Authors, object.cc BKE_object_empty_image_data_is_visible_in_view3d,
// v5.0.1, GPL-2.0-or-later. The normalized local Z axis projects onto the view plane.
int af_images_axis_aligned(const double* frames,int count,const double* view_axis,int* visible) {
    try {
        if(count<0||!view_axis||(count&&(!frames||!visible))) throw std::runtime_error("Invalid image view arrays.");
        const af::V3 view=Eigen::Map<const af::V3>(view_axis);
        if(!view.allFinite()||view.norm()<1e-15) throw std::runtime_error("Invalid image view axis.");
        const af::V3 direction=view.normalized();
        for(int i=0;i<count;++i) {
            const af::M4 frame=Eigen::Map<const af::M4>(frames+16*i);
            const af::V3 axis=frame.block<3,1>(0,2).normalized();
            visible[i]=frame.allFinite()&&axis.squaredNorm()>0&&(axis-direction*axis.dot(direction)).squaredNorm()<=1e-5;
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_images_pick(const double* frames,const double* sizes,const int* sides,int count,
                  const double* origin,const double* direction,double* hits) {
    try {
        if(count<0||!origin||!direction||(count&&(!frames||!sizes||!sides||!hits))) throw std::runtime_error("Invalid image picking arrays.");
        const af::V3 p=Eigen::Map<const af::V3>(origin), d=Eigen::Map<const af::V3>(direction);
        if(!p.allFinite()||!d.allFinite()||d.norm()<1e-15) throw std::runtime_error("Invalid image picking ray.");
        int found=0;
        for(int i=0;i<count;++i) if(af::image_hit(Eigen::Map<const af::M4>(frames+i*16),sizes+i*2,sides[i],p,d.normalized(),hits+found*8)) {
            hits[found*8]=i; ++found;
        }
        return found;
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
int af_image_vertices(uint64_t handle,int tile,double width,double height,float* output) {
    try {
        if(!output||!std::isfinite(width)||!std::isfinite(height)||width<=0||height<=0) throw std::runtime_error("Invalid image size.");
        const unsigned char* data=nullptr; int info[4]; uint64_t size[4];
        if(af_image_info(handle,size)||af_image_tile(handle,tile,&data,info)) return 1;
        af::image_quad(info,size,width,height,output); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
