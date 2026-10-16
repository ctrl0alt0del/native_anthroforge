// Cached point/segment AABBs; precise finite-segment tests, independent of Qt picking.
#include "construction_internal.hpp"
#include <unordered_set>

namespace af {
using Edges=Eigen::Matrix<int,Eigen::Dynamic,2,Eigen::RowMajor>;
using ComponentTree=igl::AABB<Vertices,3>;
struct ComponentIndex { Vertices vertices; Edges edges; ComponentTree tree; std::vector<int> labels; };
struct ComponentRay { V3 origin,direction; double radius; };
static double segment_distance(const V3& a,const V3& b,const ComponentRay& ray,double& along) {
    const V3 edge=b-a,offset=ray.origin-a;
    const double length=edge.squaredNorm(),projection=ray.direction.dot(edge);
    const double origin_projection=ray.direction.dot(offset),edge_offset=edge.dot(offset);
    const double determinant=length-projection*projection;
    double parameter=determinant>1e-20?(edge_offset-projection*origin_projection)/determinant:0;
    parameter=std::clamp(parameter,0.0,1.0);
    along=std::max(0.0,projection*parameter-origin_projection);
    if(along==0&&length>1e-20) parameter=std::clamp(edge_offset/length,0.0,1.0);
    return (ray.origin+along*ray.direction-a-parameter*edge).squaredNorm();
}
static bool intersects(const Eigen::AlignedBox<double,3>& box,const ComponentRay& ray) {
    double near=0,far=std::numeric_limits<double>::infinity();
    for(int axis=0;axis<3;++axis) {
        const double lower=box.min()[axis]-ray.radius-ray.origin[axis];
        const double upper=box.max()[axis]+ray.radius-ray.origin[axis];
        if(std::abs(ray.direction[axis])<1e-20) { if(lower>0||upper<0) return false; }
        else {
            const double a=lower/ray.direction[axis],b=upper/ray.direction[axis];
            near=std::max(near,std::min(a,b)); far=std::min(far,std::max(a,b));
            if(near>far) return false;
        }
    }
    return true;
}
static void query(const ComponentIndex& index,const ComponentTree& tree,const ComponentRay& ray,std::vector<std::pair<double,int>>& hits) {
    if(!intersects(tree.m_box,ray)) return;
    if(tree.m_primitive>=0) {
        const int element=tree.m_primitive; double along=0;
        const V3 a=index.vertices.row(index.edges(element,0)),b=index.vertices.row(index.edges(element,1));
        if(segment_distance(a,b,ray,along)<=ray.radius*ray.radius)
            hits.emplace_back(along,index.labels[element]);
    } else {
        if(tree.m_left) query(index,*tree.m_left,ray,hits);
        if(tree.m_right) query(index,*tree.m_right,ray,hits);
    }
}
static void build(ComponentIndex& index,const double* points,int count,bool segments,const int* labels) {
    index.vertices=Eigen::Map<const Vertices>(points,count*(segments?2:1),3);
    if(!index.vertices.allFinite()) throw std::runtime_error("Picking coordinates must be finite.");
    index.edges.resize(count,2);
    for(int i=0;i<count;++i) {
        index.edges(i,0)=segments?2*i:i; index.edges(i,1)=segments?2*i+1:i;
        index.labels.push_back(labels?labels[i]:i);
    }
    if(count) index.tree.init(index.vertices,index.edges);
}
static int pick(const ComponentIndex& index,const ComponentRay& ray,int depth) {
    if(index.labels.empty()) return -1;
    std::vector<std::pair<double,int>> hits;
    query(index,index.tree,ray,hits); std::sort(hits.begin(),hits.end());
    std::vector<int> unique; std::unordered_set<int> found;
    for(const auto& hit:hits) if(found.insert(hit.second).second) unique.push_back(hit.second);
    return unique.empty()?-1:unique[std::max(0,depth)%unique.size()];
}
}
uint64_t af_component_index_create(const double* points,int count,int segments,const int* labels) {
    try {
        if(count<0||(!points&&count)) throw std::runtime_error("Invalid picking input.");
        auto index=std::make_unique<af::ComponentIndex>();
        af::build(*index,points,count,segments!=0,labels);
        return reinterpret_cast<uint64_t>(index.release());
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
void af_component_index_release(uint64_t handle) { delete reinterpret_cast<af::ComponentIndex*>(handle); }
int af_component_index_pick(uint64_t handle,const double* origin,const double* direction,double radius,int depth) {
    const af::V3 ray(direction);
    if(!handle||ray.squaredNorm()<1e-20||radius<0) return -1;
    return af::pick(*reinterpret_cast<af::ComponentIndex*>(handle),{af::V3(origin),ray.normalized(),radius},depth);
}
