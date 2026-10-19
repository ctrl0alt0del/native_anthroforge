#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

namespace af::tissue::kernel {
inline thread_local uint64_t cancellation=0,ticks=0;
struct CancelScope {
    uint64_t previous;
    explicit CancelScope(uint64_t token):previous(cancellation) { cancellation=token; ticks=0; }
    ~CancelScope() { cancellation=previous; }
};
inline void checkpoint() {
    if(cancellation&&(++ticks&4095)==0) af::check_cancel(cancellation);
}
struct Vec { double x,y,z; };
inline Vec add(Vec a,Vec b) { checkpoint(); return {a.x+b.x,a.y+b.y,a.z+b.z}; }
inline Vec sub(Vec a,Vec b) { return {a.x-b.x,a.y-b.y,a.z-b.z}; }
inline Vec mul(Vec a,double b) { return {a.x*b,a.y*b,a.z*b}; }
inline double dot(Vec a,Vec b) { return a.x*b.x+a.y*b.y+a.z*b.z; }
inline double norm(Vec a) { checkpoint(); return std::sqrt(dot(a,a)); }
inline Vec cross(Vec a,Vec b) { return {a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x}; }
inline Vec af_vec(const double* a) { return {a[0],a[1],a[2]}; }
}
