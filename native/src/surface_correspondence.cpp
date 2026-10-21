// SPDX-License-Identifier: GPL-3.0-or-later
// Explicit material stations from addon free_surface_stations.py; numerical mapping is native.
#include "curve_surface_internal.hpp"

namespace af::curve_surface {
static void validate_mapping(const Row& row,const AfSurfaceRow& input,bool exact) {
    if(!exact||row.closed||input.start!=0||input.span!=1)
        throw std::runtime_error("Authored material correspondence requires exact complete open curves; Realign to reset.");
    const int n=input.station_count;
    if(n<2||n>4096||!input.station_parameters||!input.station_values)
        throw std::runtime_error("Invalid material correspondence buffers.");
    if(input.station_parameters[0]!=0||input.station_parameters[n-1]!=row.extent-1||input.station_values[0]!=0)
        throw std::runtime_error("Material correspondence must retain both curve endpoints.");
    for(int i=0;i<n;++i)
        if(!std::isfinite(input.station_parameters[i])||!std::isfinite(input.station_values[i])||
           (i&&(input.station_parameters[i]<=input.station_parameters[i-1]||input.station_values[i]<=input.station_values[i-1])))
            throw std::runtime_error("Material correspondence must be finite and strictly increasing.");
}
static double mapped_station(double parameter,const AfSurfaceRow& input) {
    const auto* begin=input.station_parameters;
    const auto* found=std::lower_bound(begin+1,begin+input.station_count,parameter);
    const auto b=std::min(int(found-begin),input.station_count-1),a=b-1;
    const double t=(parameter-begin[a])/(begin[b]-begin[a]);
    return (1-t)*input.station_values[a]+t*input.station_values[b];
}
void apply_correspondence(Row& row,const AfSurfaceRow& input,bool exact) {
    if(!input.station_count) return;
    validate_mapping(row,input,exact);
    const double end=input.station_values[input.station_count-1];
    for(const double parameter:row.parameters) {
        const double value=mapped_station(parameter,input)/end;
        row.material_stations.push_back(input.reverse?1-value:value);
    }
}
}
