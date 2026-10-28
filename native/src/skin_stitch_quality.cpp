#include "skin_stitch.hpp"
#include <igl/tri_tri_intersect.h>
namespace af::skin_stitch {
static bool shared(const Quad& a,const Quad& b) {
    for(const auto i:a) if(std::find(b.begin(),b.end(),i)!=b.end()) return true;
    return false;
}
static bool overlaps(const Mesh& mesh,int a,int b) {
    const auto first=mesh.triangles.row(a),second=mesh.triangles.row(b);
    bool coplanar=false; Eigen::RowVector3d start,end;
    return igl::tri_tri_intersection_test_3d(mesh.vertices.row(first[0]),mesh.vertices.row(first[1]),mesh.vertices.row(first[2]),
        mesh.vertices.row(second[0]),mesh.vertices.row(second[1]),mesh.vertices.row(second[2]),coplanar,start,end);
}
static int intersections(const Quads& quads,uint64_t cancel) {
    Faces faces; for(const auto& face:quads.faces) faces.emplace_back(face.begin(),face.end());
    const auto mesh=make_mesh(quads.points,faces,cancel,false); std::vector<Eigen::AlignedBox3d> boxes(mesh->triangles.rows());
    for(int i=0;i<mesh->triangles.rows();++i) for(int j=0;j<3;++j) boxes[i].extend(V3(mesh->vertices.row(mesh->triangles(i,j))));
    std::set<std::pair<int64_t,int64_t>> hits;
    for(int i=0;i<mesh->triangles.rows();++i) {
        check_cancel(cancel);
        for(int j=i+1;j<mesh->triangles.rows();++j) {
            const auto a=mesh->polygons[i],b=mesh->polygons[j];
            if(a==b||shared(quads.faces[a],quads.faces[b])||!boxes[i].intersects(boxes[j])) continue;
            if(overlaps(*mesh,i,j)) hits.insert(std::minmax(a,b));
        }
    }
    return int(hits.size());
}
void quality(Transition& transition,uint64_t cancel) {
    std::vector<double> aspects;
    for(const auto& face:transition.mesh.faces) {
        double smallest=INFINITY,largest=0;
        for(int i=0;i<4;++i) {
            const double length=(transition.mesh.points[face[i]]-transition.mesh.points[face[(i+1)%4]]).norm();
            smallest=std::min(smallest,length); largest=std::max(largest,length);
        }
        aspects.push_back(largest/std::max(smallest,1e-12));
    }
    if(aspects.empty()) throw std::runtime_error("Skin transition contains no quads.");
    std::sort(aspects.begin(),aspects.end()); const double at=.95*(aspects.size()-1);
    transition.p95=aspects[size_t(at)]+(at-std::floor(at))*(aspects[size_t(std::ceil(at))]-aspects[size_t(at)]);
    transition.maximum=aspects.back(); transition.intersections=intersections(transition.mesh,cancel);
}
}
