#include "construction_internal.hpp"

namespace af {
std::shared_ptr<Mesh> make_mesh(const Points& points,const Faces& faces,uint64_t cancel,bool complete) {
    auto result=std::make_shared<Mesh>();
    result->generated=true;
    result->vertices.resize(points.size(),3);
    for(size_t i=0;i<points.size();++i) result->vertices.row(i)=points[i];
    prepare_mesh(*result,faces,cancel,complete);
    return result;
}
Faces mesh_faces(const Mesh& source) {
    Faces result;
    for(size_t i=1;i<source.offsets.size();++i)
        result.emplace_back(source.corners.begin()+source.offsets[i-1],source.corners.begin()+source.offsets[i]);
    return result;
}
std::shared_ptr<Mesh> deform_mesh(const Mesh& source,const Vertices& vertices,uint64_t cancel,bool complete) {
    if(vertices.rows()!=source.vertices.rows()||!vertices.allFinite())
        throw std::runtime_error("Deformation must preserve vertex count and finite coordinates.");
    auto result=std::make_shared<Mesh>();
    result->vertices=vertices;
    result->generated=true;
    result->triangles=source.triangles;
    result->corners=source.corners;
    result->offsets=source.offsets;
    result->polygons=source.polygons;
    check_cancel(cancel);
    if(complete) rebuild_mesh(*result,cancel);
    else af_bounds3d(vertices.data(),vertices.rows(),result->bounds);
    return result;
}
Samples read_samples(const double* values,int count) {
    if(!values||count<2) throw std::runtime_error("At least two curve samples are required.");
    Samples samples;
    for(int i=0;i<count;++i) {
        const double* p=values+i*11;
        samples.push_back({V3(p),V3(p+3),V3(p+6),p[9],p[10]});
    }
    return samples;
}
static std::shared_ptr<Mesh> join_meshes(const uint64_t* sources,int count,uint64_t cancel) {
    Points points; Faces faces; bool complete=true;
    for(int i=0;i<count;++i) {
        check_cancel(cancel);
        const auto source=mesh(sources[i]); const auto offset=int64_t(points.size());
        complete=complete&&source->prepared;
        for(int j=0;j<source->vertices.rows();++j) points.push_back(source->vertices.row(j));
        for(auto face:mesh_faces(*source)) {
            for(auto& index:face) index+=offset;
            faces.push_back(std::move(face));
        }
    }
    return make_mesh(points,faces,cancel,complete);
}
}
uint64_t af_mesh_deformed(uint64_t source,const double* points,int64_t count,uint64_t cancel) {
    try {
        const auto input=af::mesh(source);
        return af::retain(af::deform_mesh(*input,Eigen::Map<const af::Vertices>(points,count,3),cancel,input->prepared));
    } catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
uint64_t af_mesh_join(const uint64_t* sources,int count,uint64_t cancel) {
    try { return af::retain(af::join_meshes(sources,count,cancel)); }
    catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
int af_matrix_relative(const double* frame,const double* world,double* output) {
    try {
        Eigen::Map<af::M4> result(output);
        result=Eigen::Map<const af::M4>(frame).inverse()*Eigen::Map<const af::M4>(world);
        if(!result.allFinite()) throw std::runtime_error("Singular control frame.");
        result.row(3)=Eigen::Vector4d(0,0,0,1);
        return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
int af_matrix_product(const double* a,const double* b,double* output) {
    Eigen::Map<af::M4> result(output);
    result=Eigen::Map<const af::M4>(a)*Eigen::Map<const af::M4>(b);
    return 0;
}
