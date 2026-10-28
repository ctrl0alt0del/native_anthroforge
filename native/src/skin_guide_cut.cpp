#include "skin_annuli.hpp"
#include "skin_ring.hpp"
#include "anthroforge/skin_annuli.h"
namespace af::skin_annuli {
Vertices outer_ring(const Patch& patch) {
    double length=-1; int best=0;
    for(int row=0;row<rows;++row) {
        const double current=skin_loops::perimeter(patch.points.middleRows(row*patch.segments,patch.segments));
        if(current>length) { length=current; best=row; }
    }
    return patch.points.middleRows(best*patch.segments,patch.segments);
}
static bool cut_face(const skin_ring::Projection& projection,const V3& center) {
    const V3 delta=center-projection.center;
    return delta.norm()<1.8*projection.radius&&std::abs(delta.dot(projection.normal))<.55*projection.radius
        &&skin_ring::inside(projection,center);
}
static std::vector<skin_ring::Projection> projections(const Patches& patches,const Plane& plane,double diagonal) {
    std::vector<skin_ring::Projection> result;
    for(const auto& patch:patches) {
        const auto ring=outer_ring(patch); const double scale=skin_ring::centered(ring,plane,diagonal)?1:1.08;
        result.push_back(skin_ring::project(ring,scale));
    }
    return result;
}
static Faces remaining(const Mesh& mesh,const std::vector<skin_ring::Projection>& rings,uint64_t cancel) {
    Faces result; const auto faces=mesh_faces(mesh);
    for(size_t i=0;i<faces.size();++i) {
        if(i%256==0) check_cancel(cancel);
        V3 center=V3::Zero(); for(const auto vertex:faces[i]) center+=mesh.vertices.row(vertex);
        center/=faces[i].size(); bool removed=false;
        for(const auto& ring:rings) if(cut_face(ring,center)) { removed=true; break; }
        if(!removed) result.push_back(faces[i]);
    }
    return result;
}
static std::shared_ptr<Mesh> cut(const Mesh& source,const Patches& patches,const Plane& plane,uint64_t cancel) {
    const double diagonal=std::max((source.vertices.colwise().maxCoeff()-source.vertices.colwise().minCoeff()).norm(),1e-9);
    const auto rings=projections(patches,plane,diagonal); const auto faces=remaining(source,rings,cancel);
    if(faces.empty()) throw std::runtime_error("Topology guide holes removed the entire remeshing surface.");
    Points points; points.reserve(source.vertices.rows());
    for(int i=0;i<source.vertices.rows();++i) points.push_back(source.vertices.row(i));
    return make_mesh(points,faces,cancel);
}
}
uint64_t af_skin_cut_guides(uint64_t mesh,uint64_t annuli,const double* plane,uint64_t cancel) {
    try {
        af::check_cancel(cancel); const auto patches=af::skin_annuli::get(annuli); const auto source=af::mesh(mesh);
        if(patches->empty()) return af::retain(source);
        return af::retain(af::skin_annuli::cut(*source,*patches,af::skin_loops::plane(plane),cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
