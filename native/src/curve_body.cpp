#include "construction_internal.hpp"

namespace af {
static V3 profile_point(const CurveSample& sample,int side,int sides,int shape,double width,double depth) {
    const double angle=2*M_PI*side/sides;
    const double u=shape==0?(side==0||side==3?-1:1):std::cos(angle);
    const double v=shape==0?(side<2?-1:1):std::sin(angle);
    const V3 binormal=sample.tangent.cross(sample.normal).normalized();
    return sample.position+sample.radius*(sample.normal*width*u+binormal*depth*v)*0.5;
}
static double capsule_scale(double position,double length,double radius) {
    const double x=std::min(position,length-position)/radius;
    return x>=1?1:std::sqrt(std::max(0.0,1-(1-x)*(1-x)));
}
static Points body_points(const Samples& samples,int shape,int sides,double width,double depth,bool closed) {
    Points points;
    const double length=(samples.back().position-samples.front().position).norm();
    const double radius=std::min(length,std::max(width,depth))*0.5;
    for(size_t i=0;i<samples.size();++i) {
        const double distance=(samples[i].position-samples.front().position).norm();
        const double scale=shape==2&&!closed?capsule_scale(distance,length,radius):1;
        if(scale==0) { points.push_back(samples[i].position); continue; }
        for(int j=0;j<sides;++j)
            points.push_back(profile_point(samples[i],j,sides,shape,width*scale,depth*scale));
    }
    return points;
}
static void body_strip(Faces& faces,int a,int b,int sides,bool first,bool last) {
    for(int j=0;j<sides;++j) {
        const int next=(j+1)%sides;
        if(first) faces.push_back({a,b+next,b+j});
        else if(last) faces.push_back({a+j,a+next,b});
        else faces.push_back({a+j,a+next,b+next,b+j});
    }
}
static void body_caps(Faces& faces,int count,int sides) {
    std::vector<int64_t> first,last;
    for(int j=0;j<sides;++j) { first.push_back(sides-1-j); last.push_back((count-1)*sides+j); }
    faces.push_back(std::move(first));
    faces.push_back(std::move(last));
}
static Faces body_faces(int count,int sides,bool capsule,bool closed) {
    Faces faces;
    int a=0;
    for(int i=0;i<count-(closed?0:1);++i) {
        const bool first=capsule&&i==0,last=capsule&&i==count-2;
        const int b=(i+1==count)?0:a+(first?1:sides);
        body_strip(faces,a,b,sides,first,last); a=b;
    }
    if(!closed&&!capsule) body_caps(faces,count,sides);
    return faces;
}
static double capsule_position(int i,int count,double length,double radius) {
    const int cap=std::max(1,(count-1)/4);
    if(i<=cap) return radius*(1-std::cos(M_PI_2*i/cap));
    if(i>=count-1-cap) return length-radius*(1-std::cos(M_PI_2*(count-1-i)/cap));
    return radius+(length-2*radius)*(i-cap)/(count-1-2*cap);
}
static Samples base_samples(int count,int shape,double length,double radius,bool closed) {
    Samples samples;
    for(int i=0;i<count;++i) {
        const double x=shape==2&&!closed?capsule_position(i,count,length,radius):length*i/(closed?count:count-1);
        samples.push_back({V3(x,0,0),V3::UnitX(),V3::UnitY(),1,0});
    }
    return samples;
}
}
uint64_t af_body_base(int count,int shape,int sides,double width,double depth,double length,int closed,uint64_t cancel) {
    try {
        if(shape<0||shape>2||sides<3||width<=0||depth<=0||length<=0||count<3)
            throw std::runtime_error("Invalid body base settings.");
        const double radius=std::min(length,std::max(width,depth))*0.5;
        const auto samples=af::base_samples(count,shape,length,radius,closed!=0);
        if(shape==0) sides=4;
        const auto points=af::body_points(samples,shape,sides,width,depth,closed!=0);
        const auto faces=af::body_faces(count,sides,shape==2&&!closed,closed!=0);
        return af::retain(af::make_mesh(points,faces,cancel));
    } catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
