// SPDX-License-Identifier: GPL-3.0-or-later
#include "curve_surface_internal.hpp"

namespace af::curve_surface {
static Row authored_row(const AfSurfaceRow& input) {
    const auto source=path(input.path);
    Row result; result.closed=source->closed; result.parameters=source->parameters;
    result.extent=std::floor(result.parameters.back())+1;
    const auto frame=Eigen::Map<const M4>(input.matrix);
    if(!frame.allFinite()) throw std::runtime_error("Surface transform must be finite.");
    for(size_t i=0;i<source->parameters.size();++i)
        result.points.push_back(point(frame,V3(source->samples.data()+11*i)));
    return result;
}
static double distance(double a,double b,const Row& row) {
    const double value=(b-a)*row.direction;
    return value<0?value+row.extent:value;
}
static std::pair<size_t,double> origin_edge(const Row& row,double origin) {
    if(!std::isfinite(origin)||origin<0||origin>=row.extent)
        throw std::runtime_error("Closed surface correspondence is stale; explicitly Realign.");
    for(size_t a=0;a<row.parameters.size();++a) {
        const size_t b=(a+1)%row.parameters.size();
        const double width=distance(row.parameters[a],row.parameters[b],row),offset=distance(row.parameters[a],origin,row);
        if(offset==0||(offset<width&&width>0)) return {a,width>0?offset/width:0};
    }
    throw std::runtime_error("Closed surface correspondence cannot be located.");
}
static Row rotate(const Row& row,double origin) {
    if(origin<0) return row;
    const auto edge=origin_edge(row,origin); const size_t a=edge.first,b=a+1;
    const double t=edge.second;
    Row result; result.closed=true; result.extent=row.extent; result.direction=row.direction;
    result.points.push_back((1-t)*row.points[a]+t*row.points[b%row.points.size()]);
    result.parameters.push_back(origin);
    for(size_t i=b;i<b+row.points.size()-size_t(t==0);++i) {
        result.points.push_back(row.points[i%row.points.size()]); result.parameters.push_back(row.parameters[i%row.points.size()]);
    }
    return result;
}
static Row oriented(Row row,bool reverse) {
    if(reverse) {
        const auto offset=row.closed?1:0;
        std::reverse(row.points.begin()+offset,row.points.end());
        std::reverse(row.parameters.begin()+offset,row.parameters.end());
        row.direction=-row.direction;
    }
    return row;
}
static void validate(const AfSurfaceRow& input) {
    if(!std::isfinite(input.start)||!std::isfinite(input.span)||input.start<0||input.start>1||input.span<=0||input.span>1)
        throw std::runtime_error("Surface range must be within normalized path length.");
    if(input.samples<2||input.samples>4096) throw std::runtime_error("Invalid surface sampling density.");
}
static double parameter(const Row& row,const std::vector<double>& positions,double factor) {
    const auto found=std::lower_bound(positions.begin()+1,positions.end(),factor);
    const size_t b=std::min(size_t(found-positions.begin()),positions.size()-1),a=b-1;
    const double t=(factor-positions[a])/std::max(1e-12,positions[b]-positions[a]);
    const double end=row.parameters[b%row.parameters.size()];
    const double delta=row.closed?distance(row.parameters[a],end,row)*row.direction:end-row.parameters[a];
    return std::fmod(row.parameters[a]+t*delta+row.extent,row.extent);
}
static Row uniform(const Row& row,int count) {
    Row result; result.closed=row.closed; result.extent=row.extent; result.direction=row.direction;
    const auto positions=stations(row);
    for(int i=0;i<count;++i) {
        const double factor=double(i)/(count-int(!row.closed));
        result.points.push_back(sample(row,positions,factor));
        result.parameters.push_back(parameter(row,positions,factor));
    }
    return result;
}
static void append_range(Row& result,const Row& row,const std::vector<double>& positions,double start,double span) {
    for(size_t i=1;i<row.points.size()*(row.closed?2:1);++i) {
        const double factor=positions[i%row.points.size()]+double(i/row.points.size());
        if(factor>start&&factor<start+span) {
            result.points.push_back(row.points[i%row.points.size()]); result.parameters.push_back(row.parameters[i%row.points.size()]);
        }
    }
}
static Row range(const Row& row,double start,double span) {
    if(start==0&&span==1) return row;
    if(!row.closed&&start+span>1+1e-12) throw std::runtime_error("Open surface range exceeds path.");
    Row result; result.closed=row.closed&&span==1; result.extent=row.extent; result.direction=row.direction;
    const auto positions=stations(row);
    result.points.push_back(sample(row,positions,start));
    result.parameters.push_back(parameter(row,positions,start));
    append_range(result,row,positions,start,span);
    if(!result.closed) {
        const double end=row.closed?std::fmod(start+span,1.):start+span;
        result.points.push_back(sample(row,positions,end)); result.parameters.push_back(parameter(row,positions,end));
    }
    return result;
}
static int sampling_count(const AfSurfaceRow* data,int count) {
    int samples=2; size_t total=0;
    for(int i=0;i<count;++i) {
        validate(data[i]); samples=std::max(samples,data[i].samples);
        total+=path(data[i].path)->parameters.size();
        if(total>max_vertices) throw std::runtime_error("Surface source sample budget exceeded.");
    }
    return samples;
}
Rows inputs(const AfSurfaceRow* data,int count,bool exact,uint64_t cancel) {
    if(!data||count<1||count>1024) throw std::runtime_error("Invalid surface source count.");
    const int samples=sampling_count(data,count);
    Rows result;
    for(int i=0;i<count;++i) {
        check_cancel(cancel); validate(data[i]);
        auto row=range(oriented(authored_row(data[i]),data[i].reverse!=0),data[i].start,data[i].span);
        if(row.closed) row=oriented(rotate(row,data[i].origin),data[i].alignment_reverse!=0);
        if(!exact) row=uniform(row,std::max(samples,row.closed?3:2));
        apply_correspondence(row,data[i],exact);
        if(!result.empty()&&row.closed!=result.front().closed) throw std::runtime_error("Incompatible surface ranges/closure.");
        result.push_back(std::move(row));
    }
    return result;
}
}
