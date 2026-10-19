#pragma once
#include <cstdint>

namespace af::routing {
// NumPy PCG64 streams used by the accepted deterministic pin-exit policy.
class Random {
    uint64_t high_,low_,increment_high_,increment_low_;
    uint32_t buffered_=0;
    bool has_buffer_=false;
    uint64_t next64();
    uint32_t next32();
public:
    explicit Random(bool forest=false);
    double uniform(double distance);
    uint32_t index(uint32_t count);
};
}
