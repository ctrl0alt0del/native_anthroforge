#include "skin_reconstruction.hpp"

namespace af::skin {
void diagnose(Tiles& tiles,const Mesh& mesh,double* output,uint64_t cancel) {
    const auto* vertices=mesh.vertices.data(); const auto* faces=mesh.corners.data();
    const int nv=int(mesh.vertices.rows()),nf=int(mesh.corners.size()/3); check_cancel(cancel);
    if(!kernel::af_skin_mesh_quality(vertices,nv,faces,nf,output+1)) output[0]+=1;
    check_cancel(cancel);
    if(!kernel::af_skin_tiles_validate(&tiles,vertices,nv,faces,nf,output+10)) output[0]+=2;
    check_cancel(cancel); int64_t intersections=0;
    if(!kernel::af_skin_source_intersections(tiles.scene,&intersections)) {
        output[0]+=4; output[17]=double(intersections);
    }
    check_cancel(cancel);
}
}
