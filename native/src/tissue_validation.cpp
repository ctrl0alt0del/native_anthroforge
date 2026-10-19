// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_inflation.hpp"

namespace af::tissue {
static void range(double value,double low,double high,const char* label) {
    if(!std::isfinite(value)||value<low||value>high) throw std::runtime_error(label);
}
static void profile_settings(const AfTissueInflation& s,const MaterialGrid& grid) {
    if(grid.closed_u||grid.closed_v||grid.rows<3||grid.columns<3)
        throw std::runtime_error("Section Profile requires an ordinary open loft with at least three samples per axis.");
    for(int i=0;i<4;++i) {
        range(s.profile[i],0,10,"Invalid Section Profile depth.");
        range(s.profile[i+4],.1,.9,"Invalid Section Profile peak.");
    }
    range(s.profile[8],.25,4,"Invalid Section Profile roundness.");
    if(s.direction<0||s.direction>2) throw std::runtime_error("Invalid Section Profile direction.");
}
void validate_inflation(const AfTissueInflation& s,const MaterialGrid& grid) {
    if(s.mode<0||s.mode>2||s.falloff<0||s.falloff>2) throw std::runtime_error("Invalid inflation mode or falloff.");
    if(s.mode==2) profile_settings(s,grid);
    range(s.amount,0,1000,"Invalid inflation amount.");
    range(s.radius,0,1000,"Invalid control radius.");
    range(s.depth,-1000,1000,"Invalid control depth.");
    range(s.boundary_strength,0,1,"Invalid boundary strength.");
    range(s.boundary_band,0,1000,"Invalid boundary band.");
    range(s.boundary_power,1e-12,1000,"Invalid boundary power.");
    range(s.taper,0,1000,"Invalid longitudinal taper.");
    for(double value:s.control) if(!std::isfinite(value)) throw std::runtime_error("Invalid inflation control.");
}
}
