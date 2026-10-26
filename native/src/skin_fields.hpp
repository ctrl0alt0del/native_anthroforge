#pragma once
#include <array>
#include <cstdint>
#include <vector>

namespace af::skin {
using Mask=std::vector<uint8_t>;
using Values=std::vector<double>;
struct Grid {
    std::array<int,3> shape{};
    std::array<double,3> origin{};
    double voxel=0,length=0;
    int resolution=0;
    uint64_t count=0,cancel=0;
};
struct Fields { Grid grid; std::array<Values,4> values; };
struct Source {
    const double* vertices; int count; const int64_t* faces; int triangles;
    const uint8_t* skeletal; const double* collagen;
};
struct Raster { Mask all,skeletal; std::vector<float> seeds; };
Grid grid(const Source& source,const double* settings,int resolution,uint64_t budget,uint64_t cancel);
Raster raster(const Grid& grid,const Source& source);
Mask dilate(const Grid& grid,const Mask& input);
Values distance(const Grid& grid,const Mask& seeds);
Values exterior(const Grid& grid,const Mask& surface,double probe,double offset);
Values collagen(const Grid& grid,const std::vector<float>& seeds,double inner,double width);
Fields prepare(const Source& source,const double* settings,int resolution,uint64_t budget,uint64_t cancel);
uint64_t index(const Grid& grid,int x,int y,int z);
std::array<int,3> coordinates(const Grid& grid,uint64_t index);
}
