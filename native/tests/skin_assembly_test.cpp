#include "skin_buffers_test.hpp"
#include <cmath>

using namespace af;
using namespace af::skin;
static void lexicographic_first_occurrence() {
    Assembly input;
    append(input,{{2,0,0, 1.000001f,0,0, 0,1,0},{0,1,2}},{0,0,0});
    append(input,{{-0.999997f,0,0, -2,1,0, 0,0,0},{2,1,0}},{2,0,0});
    const auto mesh=assemble(input,V3(10,20,30),2);
    require_skin(mesh->vertices.rows()==3);
    require_skin(mesh->corners==std::vector<int64_t>({2,1,0,2,0,1}));
    const double first=double(float(double(1.000001f)*2+10));
    const double later=double(float((double(-0.999997f)+2)*2+10));
    require_skin(mesh->vertices(1,0)==first&&first!=later&&first!=12.0);
    require_skin(mesh->vertices.row(0).transpose()==V3(10,22,30));
    require_skin(input.vertices.empty());
}
static void five_decimal_keys() {
    Assembly input;
    append(input,{{0,0,0, 0.000004f,0,0, 0.000006f,0,0, 0,1,0},{0,2,3,1,2,3}},{0,0,0});
    const auto mesh=assemble(input,V3::Zero(),1);
    require_skin(mesh->vertices.rows()==3);
    require_skin(mesh->vertices(2,0)==double(0.000006f));
    require_skin(mesh->corners==std::vector<int64_t>({0,2,1,0,2,1}));
}
static void signed_zero_and_negative_keys() {
    Assembly input;
    append(input,{{-0.0f,0,0, -2,0,0, 0,1,0, 0.0f,0,0},{0,1,2,3,1,2}},{0,0,0});
    const auto mesh=assemble(input,V3::Zero(),1);
    require_skin(mesh->vertices.rows()==3);
    require_skin(mesh->corners==std::vector<int64_t>({1,0,2,1,0,2}));
}
static void cancelled_assembly() {
    Cancellation token; Assembly input; input.cancel=reinterpret_cast<uint64_t>(&token);
    append(input,{{0,0,0, 1,0,0, 0,1,0},{0,1,2}},{0,0,0});
    token.cancelled.store(true); bool cancelled=false;
    try { (void)assemble(input,V3::Zero(),1); }
    catch(const std::runtime_error&) { cancelled=true; }
    require_skin(cancelled&&input.vertices.size()==3);
}
void test_skin_assembly() {
    lexicographic_first_occurrence(); five_decimal_keys();
    signed_zero_and_negative_keys(); cancelled_assembly();
}
