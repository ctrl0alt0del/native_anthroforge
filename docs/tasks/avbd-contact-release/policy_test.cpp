#include <iostream>
#include <limits>
#include "contact_candidate_budget.hpp"
#include "radius_types.hpp"

void require(bool value) {
    if(!value) throw std::runtime_error("Policy assertion failed");
}
template<class F> void rejects(F operation) {
    bool rejected=false;
    try { operation(); } catch(const std::exception&) { rejected=true; }
    require(rejected);
}
void candidates() {
    require(bounded_candidate_slots(2097152,3000000,100,134217828,16)==16777216);
    require(bounded_candidate_slots(2097152,3000000,100,100,16)==8388608);
    require(bounded_candidate_slots(2097152,3000000,100,116,16)==8388609);
    require(bounded_candidate_slots(1,3000000,100,100000000,16)==3000000);
    rejects([]{bounded_candidate_slots(1,1,100,99,16);});
    rejects([]{bounded_candidate_slots(1,1,100,100,0);});
    rejects([]{minimum_candidate_slots(0,1);});
    rejects([]{minimum_candidate_slots(1,0);});
}
void radii() {
    afcuda::RadiusSettings root{.03,.0055,true,true};
    require(afcuda::initial_contact_radius(root)==.03);
    root.initial=.0065;
    require(afcuda::initial_contact_radius(root)==.0065);
    afcuda::RadiusSettings muscle{.012,.0055,false,false};
    muscle.initial=.0065;
    require(afcuda::initial_contact_radius(muscle)==.012);
    for(double value:{0.,-1.,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}) {
        root.initial=value;
        rejects([&]{afcuda::initial_contact_radius(root);});
    }
}
int main() {
    candidates();
    radii();
    std::cout<<"PASS bounded candidate capacity, root/local/fixed radius, invalid values\n";
}
