#pragma once
#include "construction_internal.hpp"
#include "anthroforge/path.h"

namespace af {
struct ComponentIndex;
struct EvaluatedPath {
    Samples samples;
    std::vector<double> parameters;
};
struct Path {
    std::vector<double> samples, parameters;
    std::vector<float> render;
    std::shared_ptr<ComponentIndex> index;
    std::array<double, 6> bounds{};
    bool closed=false;
};
constexpr int path_chunk_segments=2048;
void prepare_path(Path& path,uint64_t cancel);
EvaluatedPath authored_path(const double* records,int count,int engine,bool closed,int resolution,uint64_t cancel);
std::shared_ptr<Path> make_path(const EvaluatedPath& evaluated,bool closed,uint64_t cancel);
uint64_t retain_path(std::shared_ptr<Path> path);
std::shared_ptr<Path> path(uint64_t handle);
}
