#include "construction_internal.hpp"

namespace af {
static Points loft_points(const double* samples,int curves,int count,int strips) {
    Points points;
    for(int row=0;row<(curves-1)*strips+1;++row) {
        const int curve=std::min(row/strips,curves-2);
        const double t=double(row-curve*strips)/strips;
        for(int j=0;j<count;++j) {
            const V3 a(samples+(curve*count+j)*11),b(samples+((curve+1)*count+j)*11);
            points.push_back((1-t)*a+t*b);
        }
    }
    return points;
}
Faces grid_faces(int rows,int count,bool closed,bool close_across) {
    Faces faces;
    for(int row=0;row<rows-int(!close_across);++row)
        for(int j=0;j<count-(closed?0:1);++j) {
            const int next=(j+1)%count;
            faces.push_back({row*count+j,((row+1)%rows)*count+j,((row+1)%rows)*count+next,row*count+next});
        }
    return faces;
}
static void cap_loft(Faces& faces,int rows,int count,bool closed) {
    if(!closed) throw std::runtime_error("Capped lofts require closed cross-section curves.");
    std::vector<int64_t> first,last;
    for(int i=0;i<count;++i) { first.push_back(i); last.push_back((rows-1)*count+count-1-i); }
    faces.push_back(std::move(first));
    faces.push_back(std::move(last));
}
static uint64_t loft(const double* samples,int curves,int count,int strips,int closed,int caps,uint64_t cancel,bool complete) {
    try {
        if(!samples||curves<2||count<2||strips<1) throw std::runtime_error("Invalid loft inputs.");
        const int rows=(curves-1)*strips+1;
        const auto points=af::loft_points(samples,curves,count,strips);
        auto faces=af::grid_faces(rows,count,closed!=0);
        if(caps) af::cap_loft(faces,rows,count,closed!=0);
        return af::retain(af::make_mesh(points,faces,cancel,complete));
    } catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
}
uint64_t af_loft(const double* samples,int curves,int count,int strips,int closed,int caps,uint64_t cancel) {
    return af::loft(samples,curves,count,strips,closed,caps,cancel,true);
}
uint64_t af_loft_geometry(const double* samples,int curves,int count,int strips,int closed,int caps,uint64_t cancel) {
    return af::loft(samples,curves,count,strips,closed,caps,cancel,false);
}
