#include "skin_buffers_test.hpp"
#include "skin_execution.hpp"

// Test-only sinks isolate buffers from registry/mesh preparation and force both team sizes.
// End-to-end envelope and addon parity checks exercise the real implementations.
static int test_workers=1;
namespace af::skin {
int field_workers(uint64_t lines) { return lines<16?1:test_workers; }
}
namespace af {
void check_cancel(uint64_t token) {
    if(token&&reinterpret_cast<Cancellation*>(token)->cancelled.load())
        throw std::runtime_error("Calculation cancelled.");
}
std::shared_ptr<Mesh> make_mesh(const Points& points,const Faces& faces,uint64_t cancel,bool complete) {
    check_cancel(cancel); require_skin(!complete);
    auto result=std::make_shared<Mesh>(); result->vertices.resize(Eigen::Index(points.size()),3);
    for(size_t i=0;i<points.size();++i) result->vertices.row(Eigen::Index(i))=points[i];
    for(const auto& face:faces) result->corners.insert(result->corners.end(),face.begin(),face.end());
    return result;
}
}
int main() {
    test_skin_assembly();
    for(int workers:{1,4}) { test_workers=workers; test_skin_fields(); }
    return 0;
}
