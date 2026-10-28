// Narrow geometry-only adapter. Attribute-bearing meshes cannot enter this boundary.
#include "BKE_customdata.hh"
#include "BKE_mesh.hh"
#include "BKE_multires.hh"
#include "bmesh.hh"
#include <algorithm>
#include <stdexcept>
static void empty(const CustomData *data) {
    if(data->totlayer||data->totsize||data->pool)
        throw std::runtime_error("Skin BMesh subset cannot contain CustomData layers.");
}
static void unsupported() { throw std::runtime_error("Unsupported attribute access in the geometry-only BMesh subset."); }
void CustomData_reset(CustomData *data) { *data={}; std::fill_n(data->typemap,CD_NUMTYPES,-1); }
bool CustomData_has_interp(const CustomData *data) { empty(data); return false; }
bool CustomData_has_math(const CustomData *data) { empty(data); return false; }
bool CustomData_layer_has_math(const CustomData *,int) { unsupported(); return false; }
bool CustomData_data_equals(eCustomDataType,const void *,const void *) { unsupported(); return false; }
void CustomData_bmesh_interp_n(CustomData *,const void **,const float *,int,void *,int) { unsupported(); }
void *CustomData_bmesh_get(const CustomData *data,void *,eCustomDataType) { empty(data); return nullptr; }
int CustomData_get_offset(const CustomData *data,eCustomDataType) { empty(data); return -1; }
void CustomData_bmesh_set_default(CustomData *data,void **block) { empty(data); *block=nullptr; }
void CustomData_bmesh_copy_block(CustomData &data,void *,void **block) { empty(&data); *block=nullptr; }
void CustomData_bmesh_copy_block(CustomData &data,const BMCustomDataCopyMap &,const void *,void **block) { empty(&data); *block=nullptr; }
void CustomData_bmesh_free_block(CustomData *data,void **block) { empty(data); *block=nullptr; }
void CustomData_bmesh_interp(CustomData *data,const void **,const float *,int,void *) { empty(data); }
bool CustomData_bmesh_has_free(const CustomData *data) { empty(data); return false; }
void CustomData_free(CustomData *data) { empty(data); }
void BKE_lnor_spacearr_free(MLoopNorSpaceArray *) { unsupported(); }
void bpy_bm_generic_invalidate(BPy_BMGeneric *) { unsupported(); }
void BMO_error_clear(BMesh *bm) { if(bm->errorstack.first) unsupported(); }
void old_mdisps_bilinear(float result[3],float (*)[3],int,float,float) { (void)result; unsupported(); }
