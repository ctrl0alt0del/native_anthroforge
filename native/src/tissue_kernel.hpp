#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

namespace af::tissue::kernel {
struct Vec { double x,y,z; };
inline Vec add(Vec a,Vec b) { return {a.x+b.x,a.y+b.y,a.z+b.z}; }
inline Vec sub(Vec a,Vec b) { return {a.x-b.x,a.y-b.y,a.z-b.z}; }
inline Vec mul(Vec a,double b) { return {a.x*b,a.y*b,a.z*b}; }
inline double dot(Vec a,Vec b) { return a.x*b.x+a.y*b.y+a.z*b.z; }
inline double norm(Vec a) { return std::sqrt(dot(a,a)); }
inline Vec cross(Vec a,Vec b) { return {a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x}; }
inline Vec af_vec(const double* a) { return {a[0],a[1],a[2]}; }
#include "../migration/tissue/kernel_0.hpp"
#include "../migration/tissue/kernel_1.hpp"
#include "../migration/tissue/kernel_2.hpp"
#include "../migration/tissue/kernel_3.hpp"
}
