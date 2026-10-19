#include "path_contacts.hpp"
#include <cmath>
#include <stdexcept>

static void require(bool value) {
    if(!value) throw std::runtime_error("Path contact contract failed.");
}
static void open_contacts() {
    af::PathContacts contacts;
    af::add_contact(contacts,{0.001,0.001,0.01},0,0.005,false);
    require(contacts.nodes==std::set<int>({0,1,2}));
    require(af::tested_intervals(contacts,0).empty());
    const auto remaining=af::tested_intervals(contacts,2);
    require(remaining.size()==1&&std::abs(remaining[0].first-0.3)<1e-15&&remaining[0].second==1);
}
static void closed_contacts() {
    af::PathContacts contacts;
    af::add_contact(contacts,{1,1,1,1},0,1.25,true);
    require(contacts.nodes==std::set<int>({0,1,3}));
    require(af::tested_intervals(contacts,0).empty()&&af::tested_intervals(contacts,3).empty());
    require(af::tested_intervals(contacts,1)==af::Intervals({{0.25,1}}));
    require(af::tested_intervals(contacts,2)==af::Intervals({{0,0.75}}));
}
static void overlapping_contacts() {
    af::PathContacts contacts;
    af::add_contact(contacts,{1,1,1},0,1.6,false);
    af::add_contact(contacts,{1,1,1},3,1.6,false);
    require(af::tested_intervals(contacts,1).empty());
    require(contacts.nodes==std::set<int>({0,1,2,3}));
}
int main() {
    open_contacts(); closed_contacts(); overlapping_contacts();
    return 0;
}
