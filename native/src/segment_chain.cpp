// SPDX-License-Identifier: GPL-3.0-or-later
// Curve-to-mesh frames/sampling follow Blender 5.0.1; see BLENDER_PRIMITIVES.md.
#include "construction_internal.hpp"
#include "../boolean/exterior.hpp"

namespace af::chain {
struct Segment { double length,radius,bend; int samples,sides; };
static Segment segment(const double* values) {
    Segment result{values[0],values[1],values[2],int(values[3]),int(values[4])};
    if(!Eigen::Map<const Eigen::Matrix<double,5,1>>(values).allFinite()||result.length<0||result.radius<=0)
        throw std::runtime_error("Invalid segment dimensions.");
    if(result.samples<2||result.samples>256||result.sides<3||result.sides>128)
        throw std::runtime_error("Invalid segment resolution.");
    return result;
}
static std::vector<double> profile_table(const double* values,int count) {
    if(count<2||count>256) throw std::runtime_error("Invalid radius profile.");
    std::vector<int> modes(size_t(count),0); std::vector<double> table(514);
    if(af_curve_mapping(values,modes.data(),count,1,table.data()))
        throw std::runtime_error("Cannot evaluate radius profile.");
    return table;
}
static double profile_at(const std::vector<double>& table,double t) {
    const double position=std::clamp(t,0.,1.)*256;
    const int low=std::min(255,int(position));
    const double scale=table[2*low+1]+(position-low)*(table[2*low+3]-table[2*low+1]);
    if(!std::isfinite(scale)||scale<=0) throw std::runtime_error("Radius profile must remain positive.");
    return scale;
}
static V3 normal(const V3& tangent) {
    if(std::abs(tangent.x())+std::abs(tangent.y())<1e-4) return V3::UnitX();
    return V3(tangent.y(),-tangent.x(),0).normalized();
}
static void rings(Points& points,const Segment& segment,const V3& start,const V3& direction,
                  const std::vector<double>& table,uint64_t cancel) {
    const V3 tangent=segment.length==0?V3(V3::UnitZ()):direction;
    const V3 u=normal(tangent),v=tangent.cross(u);
    for(int row=0;row<segment.samples;++row) {
        check_cancel(cancel); const double t=double(row)/(segment.samples-1);
        const V3 center=start+t*segment.length*direction;
        const double radius=segment.radius*profile_at(table,t);
        for(int side=0;side<segment.sides;++side) {
            const double angle=2*M_PI*side/segment.sides;
            points.push_back(center+radius*(std::cos(angle)*u+std::sin(angle)*v));
        }
    }
}
static void topology(Faces& faces,const Segment& segment,int offset) {
    auto local=grid_faces(segment.samples,segment.sides,true);
    std::vector<int64_t> first,last;
    for(int i=0;i<segment.sides;++i) {
        first.push_back(segment.sides-1-i);
        last.push_back((segment.samples-1)*segment.sides+i);
    }
    local.push_back(first); local.push_back(last);
    for(auto& face:local) { for(auto& index:face) index+=offset; faces.push_back(std::move(face)); }
}
static void provenance(Mesh& result,const Mesh& source,const Eigen::VectorXi& origins,uint64_t cancel) {
    auto& material=result.triangle_material; material.source_count=source.triangles.rows();
    for(int i=0;i<result.triangles.rows();++i) {
        check_cancel(cancel); const auto original=source.triangles.row(origins[i]);
        material.origins.push_back(origins[i]);
        for(int j=0;j<3;++j) {
            const auto point=result.vertices.row(result.triangles(i,j));
            const V3 weights=barycentric(point,source.vertices.row(original[0]),source.vertices.row(original[1]),source.vertices.row(original[2]));
            material.coordinates.insert(material.coordinates.end(),weights.data(),weights.data()+3);
        }
    }
    validate_triangle_material(material,result.triangles.rows());
}
static std::shared_ptr<Mesh> united(const Mesh& source,uint64_t cancel) {
    auto flag=cancel?&reinterpret_cast<Cancellation*>(cancel)->cancelled:nullptr;
    const auto output=boolean::exterior(source.vertices,source.triangles,flag);
    Points points; Faces faces;
    for(int i=0;i<output.vertices.rows();++i) points.push_back(output.vertices.row(i));
    for(int i=0;i<output.faces.rows();++i) {
        const auto face=output.faces.row(i); faces.push_back({face[0],face[1],face[2]});
    }
    auto result=make_mesh(points,faces,cancel,false);
    provenance(*result,source,output.origins,cancel); return result;
}
static void append(Points& points,Faces& faces,const Segment& part,const V3& start,
                   const V3& direction,const std::vector<double>& table,bool unite,uint64_t cancel) {
    if(unite&&part.length==0) return;
    const int offset=int(points.size());
    rings(points,part,start,direction,table,cancel);
    topology(faces,part,offset);
}
static std::shared_ptr<Mesh> construct(const double* records,int count,double spread,bool cumulative,
                                      const std::vector<double>& table,bool unite,uint64_t cancel) {
    Points points; Faces faces; V3 start=V3::Zero(); double prior=0,angle=0;
    const V3 forward=Eigen::AngleAxisd(spread,V3::UnitZ())*V3::UnitY();
    for(int i=0;i<count;++i) {
        const auto part=segment(records+5*i);
        angle=(cumulative?angle:prior)+part.bend; prior=part.bend;
        const V3 direction=Eigen::AngleAxisd(angle,V3::UnitX())*forward;
        append(points,faces,part,start,direction,table,unite,cancel);
        start+=part.length*direction;
    }
    auto result=make_mesh(points,faces,cancel,false);
    return unite?united(*result,cancel):result;
}
}
uint64_t af_segment_chain(const double* segments,int count,double spread,int cumulative,
                          const double* profile,int profile_count,int unite,uint64_t cancel) {
    try {
        if(count<1||count>32||!std::isfinite(spread)) throw std::runtime_error("Invalid segment chain.");
        const auto table=af::chain::profile_table(profile,profile_count);
        return af::retain(af::chain::construct(segments,count,spread,cumulative!=0,table,unite!=0,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
