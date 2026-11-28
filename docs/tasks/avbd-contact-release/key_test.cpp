#include <algorithm>
#include <numeric>
#include <random>
#include <iostream>
#include "cuda_math.cuh"
#include "contact_key_parts.hpp"
std::vector<afcuda::Force> examples() {
    std::mt19937 rng(87278); std::vector<afcuda::Force> rows(200000);
    for(auto& row:rows) {
        row.key[0]=rng()%2;
        for(int k=1;k<5;++k) row.key[k]=int(rng()&0x7fffffff);
    }
    int bounds[]{0,32767,32768,55108,55109,65535,65536,2147483647};
    for(int bound:bounds) for(int kind=0;kind<2;++kind) {
        afcuda::Force f; f.key[0]=kind; for(int k=1;k<5;++k) f.key[k]=bound;
        rows.push_back(f); rows.push_back(f);
    }
    return rows;
}
int main() {
    auto rows=examples(); std::vector<int> expected(rows.size()),actual;
    std::iota(expected.begin(),expected.end(),0); actual=expected;
    std::stable_sort(expected.begin(),expected.end(),[&](int a,int b){return afcuda::Order{}(rows[a],rows[b]);});
    for(int part=0;part<2;++part)
        std::stable_sort(actual.begin(),actual.end(),[&](int a,int b){
            return afcuda::full_contact_key_part(rows[a],part)<afcuda::full_contact_key_part(rows[b],part); });
    if(actual!=expected) return 1;
    std::cout<<"PASS "<<rows.size()<<" randomized, duplicate and boundary keys match canonical order\n";
}

