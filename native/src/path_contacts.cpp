#include "path_contacts.hpp"
#include <algorithm>

namespace af {
static void walk(PathContacts& contact,const std::vector<double>& lengths,int pin,double span,int direction,bool closed) {
    const int count=int(lengths.size())+int(!closed); int node=pin; double travelled=0;
    for(int step=0;step<count-1;++step) {
        int next=node+direction; if(!closed&&(next<0||next>=count)) break;
        next=(next+count)%count; const int edge=direction<0?next:node;
        const double length=lengths[edge],fraction=std::clamp((span-travelled)/std::max(length,1e-12),0.0,1.0);
        if(fraction>0) contact.edges[edge].push_back(direction<0?std::make_pair(1-fraction,1.0):std::make_pair(0.0,fraction));
        if(travelled+length>span) break;
        contact.nodes.insert(next); travelled+=length; node=next;
    }
}
void add_contact(PathContacts& contact,const std::vector<double>& lengths,int pin,double span,bool closed) {
    contact.nodes.insert(pin);
    walk(contact,lengths,pin,span,-1,closed);
    walk(contact,lengths,pin,span,1,closed);
}
static Intervals subtract(const Intervals& source,double start,double end) {
    Intervals result;
    for(const auto& [low,high]:source) {
        if(end<=low||start>=high) { result.push_back({low,high}); continue; }
        if(start>low) result.push_back({low,std::min(start,high)});
        if(end<high) result.push_back({std::max(end,low),high});
    }
    return result;
}
Intervals tested_intervals(const PathContacts& contact,int edge) {
    Intervals result{{0,1}}; const auto found=contact.edges.find(edge);
    if(found==contact.edges.end()) return result;
    auto excluded=found->second; std::sort(excluded.begin(),excluded.end());
    for(const auto& [low,high]:excluded) result=subtract(result,low,high);
    return result;
}
}
