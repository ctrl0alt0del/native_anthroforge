#pragma once
#include "path_internal.hpp"
#include "anthroforge/fiber_deformation.h"
#include <Eigen/SparseCholesky>
namespace af::fiber {
using Sparse=Eigen::SparseMatrix<double>;
using Triplet=Eigen::Triplet<double>;
struct Region { std::vector<int> ids; V3 center; M3 inverse; double ridge; };
struct Parent {
    int alias=-1;
    uint64_t reference;
    std::shared_ptr<Mesh> mesh;
    M4 frame;
    Vertices vertices;
    std::vector<int> indices;
    std::vector<double> records;
    std::vector<Region> regions;
};
struct Map { M3 linear; V3 translation; };
struct Preparation {
    std::shared_ptr<Path> path;
    Vertices points;
    std::vector<double> arc,mass;
    std::vector<int> knots,pins,pin_owners,free,free_index;
    std::vector<Parent> parents;
    Eigen::MatrixXd weights;
    double length=0,width=0;
    Sparse laplacian,bending,coupling;
    Eigen::SimplicialLDLT<Sparse> factor;
};
std::shared_ptr<Preparation> prepare(const AfFiberReference& input,uint64_t cancel);
void prepare_parents(Preparation& value,const AfFiberReference& input,uint64_t cancel);
void prepare_weights(Preparation& value,const AfFiberReference& input,uint64_t cancel);
void prepare_reconstruction(Preparation& value,uint64_t cancel);
void evaluate(const Preparation& value,const uint64_t* meshes,const double* frames,
    const double* goals,double* output,uint64_t cancel);
M4 recovered_frame(const Preparation& value,const AfFiberReference& input,int parent);
double distance(const Preparation& value,double a,double b);
double kernel(double x);
double pin_width(const Preparation& value,int pin);
int nearest_pin(const Preparation& value,double station);
void smooth_weights(Preparation& value,const AfFiberReference& input,uint64_t cancel);
V3 curve_point(const Preparation& value,double station);
Map interpolated(const Preparation& value,const std::vector<Map>& maps,int row);
std::vector<std::vector<Map>> fit(const Preparation& value,const uint64_t* meshes,
    const double* frames,uint64_t cancel);
uint64_t bytes(const Preparation& value);
}
