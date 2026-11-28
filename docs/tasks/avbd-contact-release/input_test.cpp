#include "io.hpp"
#include <cassert>
#include <cstdio>
#include <limits>

void expect_rejected(int count,std::uintmax_t bytes) {
    try { experiment::validate_input_count(count,bytes); }
    catch(const std::runtime_error&) { return; }
    throw std::runtime_error("Invalid collider count was accepted");
}

void write_fixture(const char* path,int count) {
    std::ofstream out(path,std::ios::binary);
    int size[2]={3,1},face[3]={0,1,2};
    double points[9]={0,0,0,1,0,0,0,1,0};
    out.write(reinterpret_cast<const char*>(&count),sizeof(count));
    for(int i=0;i<count;++i) {
        out.write(reinterpret_cast<const char*>(size),sizeof(size));
        out.write(reinterpret_cast<const char*>(points),sizeof(points));
        out.write(reinterpret_cast<const char*>(face),sizeof(face));
    }
}

void read_fixture(int count) {
    const char* path="collider-reader-test.bin";
    write_fixture(path,count);
    const auto meshes=experiment::read_inputs(path);
    assert(meshes.size()==size_t(count));
    for(const auto& mesh:meshes) {
        assert(mesh.vertices.rows()==3&&mesh.faces.rows()==1);
        assert(mesh.vertices(1,0)==1&&mesh.vertices(2,1)==1&&mesh.faces(0,2)==2);
    }
    assert(std::remove(path)==0);
}

void reject_truncated_mesh() {
    const char* path="collider-truncated-test.bin";
    write_fixture(path,1);
    std::filesystem::resize_file(path,std::filesystem::file_size(path)-1);
    try { experiment::read_inputs(path); }
    catch(const std::runtime_error&) {
        assert(std::remove(path)==0);
        return;
    }
    throw std::runtime_error("Truncated collider geometry was accepted");
}

int main() {
    for(int count:{1,64,65,70,323}) read_fixture(count);
    reject_truncated_mesh();
    for(int count:{-1,0,1,65,std::numeric_limits<int>::max()}) expect_rejected(count,4);
    expect_rejected(1,47);
    experiment::validate_input_count(1,48);
    std::cout<<"PASS collider input counts, payload bounds and geometry preservation\n";
}
