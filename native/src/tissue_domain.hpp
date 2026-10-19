#pragma once
#include <cstdint>
#include <vector>

namespace af {
// Each output vertex has an exact sparse map to source material coordinates.
// 1 radial, 2 sweep, 3 normal shell, 4 single-side muscle, 5 two-side envelope.
struct TissueDomain {
    int64_t kind=0,source_count=0,ring_size=0,closed=0;
    std::vector<int64_t> offsets,indices,sides,parts,faces;
    std::vector<double> weights;
};
uint64_t tissue_storage(const TissueDomain& domain);
std::vector<int64_t> tissue_records(const TissueDomain& domain);
TissueDomain tissue_restore(const int64_t* data,int64_t count,const double* weights,int64_t entries,int64_t vertices,int64_t faces);
TissueDomain tissue_identity(int64_t kind,int64_t count,int64_t faces,int64_t copies=1);
void tissue_validate(const TissueDomain& domain,int64_t vertices,int64_t faces);
}
