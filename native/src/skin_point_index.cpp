#include "skin_ownership.hpp"
#include <numeric>
namespace af::skin_ownership {
PointIndex::PointIndex(const Vertices& vertices,const std::vector<int>& indices,uint64_t cancel) {
    check_cancel(cancel); elements.resize(indices.size());
    for(size_t i=0;i<indices.size();++i) elements[i]=indices[i];
    if(!indices.empty()) tree.init(vertices,elements);
    check_cancel(cancel);
}
static void leaf(const PointIndex& index,const Vertices& vertices,int primitive,const V3& p,std::pair<int,double>& best) {
    const int id=index.elements[primitive]; const V3 sample=vertices.row(id);
    const double distance=(sample-p).squaredNorm();
    if(distance<best.second||(distance==best.second&&(best.first<0||id<best.first))) best={id,distance};
}
static void query(const PointIndex& index,const Vertices& vertices,const igl::AABB<Vertices,3>& tree,
                  const V3& p,std::pair<int,double>& best) {
    if(tree.m_box.squaredExteriorDistance(p)>best.second) return;
    if(tree.m_primitive>=0) { leaf(index,vertices,tree.m_primitive,p,best); return; }
    auto first=tree.m_left,second=tree.m_right;
    if(first&&second&&first->m_box.squaredExteriorDistance(p)>second->m_box.squaredExteriorDistance(p)) std::swap(first,second);
    if(first) query(index,vertices,*first,p,best);
    if(second) query(index,vertices,*second,p,best);
}
std::pair<int,double> PointIndex::nearest(const Vertices& vertices,const V3& p) const {
    std::pair<int,double> best{-1,std::numeric_limits<double>::infinity()};
    if(elements.size()) query(*this,vertices,tree,p,best);
    return best;
}
}
