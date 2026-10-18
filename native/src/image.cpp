#include "mesh_internal.hpp"
#include "anthroforge/image.h"
#include <mutex>
#include <unordered_map>

namespace af {
struct ImageTile { int x,y,width,height; std::vector<unsigned char> rgba; };
struct Image { int width,height; std::vector<ImageTile> tiles; uint64_t bytes=sizeof(Image); };
static std::mutex image_mutex;
static std::unordered_map<uint64_t,std::shared_ptr<Image>> images;
static uint64_t next_image=1;
static ImageTile tile(const unsigned char* rgba,int width,int height,int x,int y,uint64_t cancel) {
    ImageTile result{x,y,std::min(256,width-x),std::min(256,height-y),{}};
    result.rgba.resize(size_t(result.width)*result.height*4);
    for(int row=0;row<result.height;++row) {
        check_cancel(cancel);
        const auto* source=rgba+(size_t(y+row)*width+x)*4;
        std::copy_n(source,result.width*4,result.rgba.data()+size_t(row)*result.width*4);
    }
    return result;
}
static std::shared_ptr<Image> image(uint64_t handle) {
    std::lock_guard<std::mutex> lock(image_mutex);
    const auto found=images.find(handle);
    if(found==images.end()) throw std::runtime_error("Unknown image resource.");
    return found->second;
}
static std::shared_ptr<Image> prepare_image(const unsigned char* rgba,int width,int height,uint64_t cancel) {
    if(!rgba||width<1||height<1||width>32768||height>32768) throw std::runtime_error("Invalid image dimensions.");
    auto result=std::make_shared<Image>(); result->width=width; result->height=height;
    result->tiles.reserve(size_t((width+255)/256)*((height+255)/256));
    for(int y=0;y<height;y+=256) for(int x=0;x<width;x+=256) {
        result->tiles.push_back(tile(rgba,width,height,x,y,cancel));
        result->bytes+=result->tiles.back().rgba.capacity();
    }
    result->bytes+=result->tiles.capacity()*sizeof(ImageTile); return result;
}
}
uint64_t af_image_create(const unsigned char* rgba,int width,int height,uint64_t cancel) {
    try {
        auto image=af::prepare_image(rgba,width,height,cancel);
        std::lock_guard<std::mutex> lock(af::image_mutex); const auto handle=af::next_image++;
        af::images.emplace(handle,std::move(image)); return handle;
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
void af_image_release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(af::image_mutex); af::images.erase(handle);
}
int af_image_info(uint64_t handle,uint64_t* info) {
    try {
        if(!info) throw std::runtime_error("Image info requires an output buffer.");
        const auto image=af::image(handle);
        info[0]=image->width; info[1]=image->height; info[2]=image->tiles.size(); info[3]=image->bytes; return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_image_tile(uint64_t handle,int tile,const unsigned char** data,int* info) {
    try {
        const auto image=af::image(handle);
        if(!data||!info||tile<0||size_t(tile)>=image->tiles.size()) throw std::runtime_error("Invalid image tile.");
        const auto& value=image->tiles[tile]; *data=value.rgba.data();
        info[0]=value.x; info[1]=value.y; info[2]=value.width; info[3]=value.height; return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_image_calibration(const double* frame,const double* dimensions,const double* landmarks,double distance,double* output) {
    try {
        if(!frame||!dimensions||!landmarks||!output||!std::isfinite(distance)||distance<=0)
            throw std::runtime_error("Invalid calibration input.");
        const af::M4 matrix=Eigen::Map<const af::M4>(frame);
        const af::V3 delta((landmarks[2]-landmarks[0])*dimensions[0],(landmarks[3]-landmarks[1])*dimensions[1],0);
        const double length=(matrix.block<3,3>(0,0)*delta).norm();
        if(!std::isfinite(length)||length<1e-15) throw std::runtime_error("Calibration landmarks must be distinct.");
        output[0]=dimensions[0]*distance/length; output[1]=dimensions[1]*distance/length; return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
