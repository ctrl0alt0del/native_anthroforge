// Cached point/segment AABBs; precise finite-segment tests, independent of Qt picking.
#include "component_index.hpp"
#include <unordered_set>

namespace af {
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
std::shared_ptr<ComponentIndex> path_index(const double* samples,int count,bool closed,uint64_t cancel) {
    auto index=std::make_shared<ComponentIndex>(); index->vertices.resize(count,3);
    const int edges=count-(closed?0:1); index->edges.resize(edges,2); index->labels.reserve(edges);
    for(int i=0;i<count;++i) {
        check_cancel(cancel); index->vertices.row(i)=V3(samples+11*i).transpose();
        if(i<edges) { index->edges.row(i)<<i,(i+1)%count; index->labels.push_back(i); }
    }
    index->tree.init(index->vertices,index->edges); check_cancel(cancel); return index;
}
uint64_t component_bytes(const ComponentIndex& index) {
    const uint64_t nodes=index.edges.rows()?2*index.edges.rows()-1:0;
    return sizeof(ComponentIndex)+index.vertices.size()*sizeof(double)+index.edges.size()*sizeof(int)
        +index.labels.capacity()*sizeof(int)+(nodes?nodes-1:0)*sizeof(ComponentTree);
}
struct WorldQuery { M4 frame; ComponentRay world,local; std::pair<double,int> best{INFINITY,-1}; };
static void world_leaf(const ComponentIndex& index,int element,WorldQuery& query) {
    const V3 a=point(query.frame,index.vertices.row(index.edges(element,0)));
    const V3 b=point(query.frame,index.vertices.row(index.edges(element,1))); double along=0;
    if(segment_distance(a,b,query.world,along)<=query.world.radius*query.world.radius&&along<query.best.first)
        query.best={along,index.labels[element]};
}
static void query_world(const ComponentIndex& index,const ComponentTree& tree,WorldQuery& query) {
    if(!intersects(tree.m_box,query.local)) return;
    if(tree.m_primitive>=0) world_leaf(index,tree.m_primitive,query);
    else {
        if(tree.m_left) query_world(index,*tree.m_left,query);
        if(tree.m_right) query_world(index,*tree.m_right,query);
    }
}
std::pair<double,int> component_nearest(const ComponentIndex& index,const M4& frame,const ComponentRay& ray) {
    const M4 inverse=frame.inverse();
    if(!inverse.allFinite()||!ray.origin.allFinite()||!ray.direction.allFinite()||ray.direction.norm()<1e-20
        ||!std::isfinite(ray.radius)||ray.radius<0) throw std::runtime_error("Invalid path picking ray or transform.");
    const ComponentRay world{ray.origin,ray.direction.normalized(),ray.radius};
    const ComponentRay local{point(inverse,ray.origin),inverse.block<3,3>(0,0)*world.direction,
        ray.radius*inverse.block<3,3>(0,0).norm()};
    WorldQuery query{frame,world,local};
    if(!index.labels.empty()) query_world(index,index.tree,query);
    return query.best;
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
