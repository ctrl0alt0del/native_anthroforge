#include "routing_random.hpp"
#ifdef _MSC_VER
#include <intrin.h>
#endif
#define PCG_FORCE_EMULATED_128BIT_MATH
#include <numpy_random/pcg64.h>
#ifdef inline
#undef inline
#endif

namespace af::routing {
// State words captured from NumPy 1.26.4 SeedSequence(914/915), not a new seed policy.
Random::Random(bool forest) {
    const uint64_t states[2][4]={
        {14974205650638028254ULL,14749881135014385146ULL,14181970730162785961ULL,14822022665510357923ULL},
        {14999116906598695794ULL,3883376040687943277ULL,8045475495350318617ULL,5330950560112829837ULL}};
    high_=states[forest][0]; low_=states[forest][1];
    increment_high_=states[forest][2]; increment_low_=states[forest][3];
}
uint64_t Random::next64() {
    pcg64_random_t state{{high_,low_},{increment_high_,increment_low_}};
    const auto result=pcg64_random_r(&state);
    high_=state.state.high; low_=state.state.low;
    return result;
}
uint32_t Random::next32() {
    if(has_buffer_) { has_buffer_=false; return buffered_; }
    const auto value=next64(); buffered_=uint32_t(value>>32); has_buffer_=true;
    return uint32_t(value);
}
double Random::uniform(double distance) {
    return -distance+2*distance*double(next64()>>11)*(1.0/9007199254740992.0);
}
uint32_t Random::index(uint32_t count) {
    if(count<=1) return 0;
    // NumPy distributions.c buffered_bounded_lemire_uint32, MIT licensed.
    const uint32_t threshold=(uint32_t(0)-count)%count;
    uint64_t product=uint64_t(next32())*count;
    while(uint32_t(product)<threshold) product=uint64_t(next32())*count;
    return uint32_t(product>>32);
}
}
