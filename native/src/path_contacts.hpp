#pragma once
#include <map>
#include <set>
#include <utility>
#include <vector>

namespace af {
using Intervals=std::vector<std::pair<double,double>>;
struct PathContacts {
    std::set<int> nodes;
    std::map<int,Intervals> edges;
};
void add_contact(PathContacts& contact,const std::vector<double>& lengths,int pin,double span,bool closed);
Intervals tested_intervals(const PathContacts& contact,int edge);
}
