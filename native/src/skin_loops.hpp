#pragma once
#include "path_internal.hpp"
#include "skin_point_index.hpp"
namespace af::skin_loops {
constexpr int sample_count=192;
using Graph=std::vector<std::vector<int>>;
struct Plane { bool enabled=false; V3 origin=V3::Zero(),normal=V3::UnitX(); };
struct Loop {
    int source=-1;
    Vertices points,normals;
    V3 center=V3::Zero();
    double perimeter=0;
    bool symmetric=false;
    std::shared_ptr<skin::PointIndex> index;
};
struct Context {
    const Mesh& mesh;
    Surface surface;
    uint64_t cancel;
    double diagonal;
    Plane plane;
    Graph graph;
    std::unique_ptr<skin::PointIndex> index;
    Context(const Mesh& source,const double* plane,uint64_t token);
};
struct Prepared { std::vector<Loop> loops; std::vector<std::pair<int,int>> pairs; std::vector<int> statuses; };
Plane plane(const double* values);
std::shared_ptr<skin::PointIndex> point_index(const Vertices& points,uint64_t cancel);
Loop projected(Context& context,const Vertices& points);
Loop resampled(const Loop& loop,int count,uint64_t cancel);
Vertices closure(Context& context,const Vertices& points);
double perimeter(const Vertices& points);
Vertices authored(const Path& path,const M4& frame,uint64_t cancel);
double directed_distance(const Loop& first,const Loop& second,uint64_t cancel);
bool symmetric(const Vertices& points,const Plane& plane,double diagonal,uint64_t cancel);
void pair(Prepared& result,uint64_t cancel);
Prepared prepare(Context& context,int count,const uint64_t* paths,const double* frames);
}
