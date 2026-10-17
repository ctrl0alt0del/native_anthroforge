#include "mesh_internal.hpp"
#include <igl/readOBJ.h>
#include <igl/readSTL.h>
#if defined(_MSC_VER) && !defined(__clang__)
#pragma warning(push)
// Happly's type dispatch contains intentional unreachable fallback branches.
#pragma warning(disable:4702)
#endif
#include <happly.h>
#if defined(_MSC_VER) && !defined(__clang__)
#pragma warning(pop)
#endif
#include <filesystem>
#include <fstream>

namespace af {
static FILE* open_obj(const std::string& path) {
#ifdef _WIN32
    FILE* file=nullptr;
    _wfopen_s(&file,std::filesystem::u8path(path).c_str(),L"rb");
    return file;
#else
    return fopen(path.c_str(),"rb");
#endif
}
static Faces read_obj(const std::string& path, Mesh& mesh) {
    std::vector<std::vector<double>> vertices,uvs,normals;
    Faces faces,texture_faces,normal_faces;
    std::vector<std::tuple<std::string,int64_t,int64_t>> materials;
    FILE* file=open_obj(path);
    if(!file||!igl::readOBJ(file,vertices,uvs,normals,faces,texture_faces,normal_faces,materials))
        throw std::runtime_error("Cannot read OBJ mesh.");
    mesh.vertices.resize(vertices.size(),3);
    for(size_t i=0;i<vertices.size();++i) {
        if(vertices[i].size()<3) throw std::runtime_error("OBJ position needs three coordinates.");
        for(int j=0;j<3;++j) mesh.vertices(i,j)=vertices[i][j];
    }
    return faces;
}
static Faces read_stl(const std::string& path, Mesh& mesh) {
    std::ifstream stream(std::filesystem::u8path(path),std::ios::binary);
    Eigen::MatrixXi triangles; Eigen::MatrixXd normals;
    if(!igl::readSTL(stream,mesh.vertices,triangles,normals))
        throw std::runtime_error("Cannot read STL mesh.");
    Faces faces;
    for(int i=0;i<triangles.rows();++i)
        faces.push_back({triangles(i,0),triangles(i,1),triangles(i,2)});
    return faces;
}
static Faces read_ply(const std::string& path, Mesh& mesh) {
    std::ifstream stream(std::filesystem::u8path(path),std::ios::binary);
    happly::PLYData ply(stream);
    const auto vertices=ply.getVertexPositions();
    mesh.vertices.resize(vertices.size(),3);
    for(size_t i=0;i<vertices.size();++i)
        for(int j=0;j<3;++j) mesh.vertices(i,j)=vertices[i][j];
    return ply.getFaceIndices<int64_t>();
}
std::shared_ptr<Mesh> read_mesh(const std::string& path,double units,bool y_up,uint64_t cancel) {
    if(!std::isfinite(units)||units<=0) throw std::runtime_error("Source unit scale must be positive.");
    auto result=std::make_shared<Mesh>();
    auto extension=std::filesystem::u8path(path).extension().string();
    std::transform(extension.begin(),extension.end(),extension.begin(),::tolower);
    Faces faces;
    if(extension==".obj") faces=read_obj(path,*result);
    else if(extension==".stl") faces=read_stl(path,*result);
    else if(extension==".ply") faces=read_ply(path,*result);
    else throw std::runtime_error("Supported primitive formats: OBJ, STL and PLY.");
    result->vertices*=units;
    if(y_up) result->vertices=(result->vertices*Eigen::AngleAxisd(M_PI/2,V3::UnitX()).toRotationMatrix().transpose()).eval();
    prepare_mesh(*result,faces,cancel);
    return result;
}
}
