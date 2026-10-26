#pragma once
#include "skin_annuli.hpp"
#include "skin_quads.hpp"
#include "skin_ring.hpp"
namespace af::skin_stitch {
using skin_quads::Quad;
using skin_quads::Edge;
using skin_quads::Quads;
using skin_loops::Plane;
using Triangle=std::array<int64_t,3>;
struct Transition {
    Quads mesh;
    int mode=0,reason=0,shift=0,candidates=1,intersections=0,boundary=0,annulus=0;
    double p95=0,maximum=0;
};
std::set<Edge> boundary(const std::vector<Quad>& faces);
std::vector<std::vector<int64_t>> boundaries(const std::vector<Quad>& faces,uint64_t cancel);
std::vector<Quad> regular_faces(const Vertices& first,const Vertices& second);
std::vector<Quad> centered_faces(const Vertices& first,const Vertices& second);
void validate(const std::vector<Quad>& faces,int first,int second);
Quads strip(const Vertices& first,const Vertices& second,std::vector<Quad> faces);
Quads weld(const std::vector<Quads>& parts,double tolerance,bool deduplicate,uint64_t cancel);
void orient(Quads& mesh,uint64_t cancel);
void quality(Transition& transition,uint64_t cancel);
Transition transition(const Vertices& first,const Vertices& second,const Plane& plane,double diagonal,uint64_t cancel);
std::vector<Quad> paired(const std::vector<Triangle>& triangles);
Quad join(const Triangle& a,const Triangle& b);
std::vector<int> moves(const Vertices& first,const Vertices& second,bool closed);
std::vector<Triangle> zipper(const std::vector<int64_t>& first,const std::vector<int64_t>& second,const std::vector<int>& moves,bool closed);
}
