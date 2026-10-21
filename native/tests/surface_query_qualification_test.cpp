#include "../boolean/qualification.hpp"
#include <stdexcept>

using namespace af::boolean;
static void require(bool condition) {
    if(!condition) throw std::runtime_error("Surface qualification contract failed.");
}
static Triangles tetrahedron() {
    Triangles result(4,3); result<<0,2,1,0,1,3,0,3,2,1,2,3; return result;
}
static Vertices points() {
    Vertices result(4,3); result<<0,0,0,1,0,0,0,1,0,0,0,1; return result;
}
static Suitability inspect(const Vertices& vertices,const Triangles& faces) {
    return qualify(vertices,faces,std::vector<uint8_t>(faces.rows(),1),nullptr);
}
static void topology() {
    auto vertices=points(); auto faces=tetrahedron();
    require(inspect(vertices,faces)==Suitability::Reusable);
    faces.row(0)=faces.row(1); require(inspect(vertices,faces)==Suitability::Topology);
    faces=tetrahedron(); vertices.row(0)=vertices.row(1);
    require(inspect(vertices,faces)==Suitability::Topology);
    vertices=points(); vertices.row(0)=(vertices.row(1)+vertices.row(2))/2;
    require(inspect(vertices,faces)==Suitability::Topology);
}
static void orientation() {
    const auto vertices=points(); auto faces=tetrahedron();
    for(int i=0;i<faces.rows();++i) faces.row(i).reverseInPlace();
    require(inspect(vertices,faces)==Suitability::Orientation);
}
static void cancellation() {
    std::atomic<bool> cancel{true}; bool cancelled=false;
    try { qualify(points(),tetrahedron(),std::vector<uint8_t>(4,1),&cancel); }
    catch(const std::runtime_error&) { cancelled=true; }
    require(cancelled);
}
int main() {
    topology(); orientation(); cancellation();
}
