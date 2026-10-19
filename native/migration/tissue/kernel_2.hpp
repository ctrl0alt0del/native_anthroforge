static Vec af_muscle_centroid(const std::vector<Vec>& points) {
    Vec value{0,0,0};for(Vec point:points)value=add(value,point);
    return mul(value,1.0/std::max<size_t>(1,points.size()));
}

static Vec af_muscle_normal(const std::vector<Vec>& points,int i,int j,int rows,int cols,Vec centroid) {
    int im=std::max(0,i-1),ip=std::min(rows-1,i+1),jm=std::max(0,j-1),jp=std::min(cols-1,j+1);
    Vec tv=sub(points[ip*cols+j],points[im*cols+j]);Vec tu=sub(points[i*cols+jp],points[i*cols+jm]);
    Vec value=cross(tv,tu);if(norm(value)<=1.0e-10)value=sub(points[i*cols+j],centroid);
    return af_muscle_unit(value);
}

static std::vector<Vec> af_muscle_normals(const std::vector<Vec>& points,int rows,int cols,bool coherent) {
    std::vector<Vec> out(points.size());Vec centroid=af_muscle_centroid(points);
    for(int i=0;i<rows;++i)for(int j=0;j<cols;++j){int index=i*cols+j;out[index]=af_muscle_normal(points,i,j,rows,cols,centroid);
        if(coherent&&index){Vec ref=j?out[index-1]:out[index-cols];if(dot(out[index],ref)<0.0)out[index]=mul(out[index],-1.0);}}
    return out;
}

static double af_muscle_edge_alpha(int i,int j,int rows,int cols,const AfMuscleInput& input,const AfMuscleOutput* output=nullptr) {
    if(output&&!output->boundary_weights.empty())return output->boundary_weights[i*cols+j];
    bool on_u=j==0||j==cols-1;bool on_v=!input.inflation_closed_v&&(i==0||i==rows-1);if(on_u||on_v)return 0.0;
    int du=cols>1?std::min(j,cols-1-j):0;int dv=input.inflation_closed_v?1000000000:(rows>1?std::min(i,rows-1-i):0);
    double edge=std::clamp(std::min(du,dv)/input.b_band,0.0,1.0);double smooth=edge*edge*(3.0-2.0*edge);
    return (1.0-input.b_strength)+input.b_strength*std::pow(smooth,input.b_power);
}

static double af_muscle_length_fade(int j,int cols,double taper) {
    double band=std::max(1.0,taper*std::max(0,cols-1));double distance=std::min(j,std::max(0,cols-1-j));
    double value=std::clamp(distance/band,0.0,1.0);return value*value*(3.0-2.0*value);
}

static double af_muscle_stability(const std::vector<Vec>& normals,int i,int j,int rows,int cols) {
    double result=1.0;bool found=false;const int offsets[4][2]={{-1,0},{1,0},{0,-1},{0,1}};
    for(auto& offset:offsets){int ii=i+offset[0],jj=j+offset[1];if(ii<0||ii>=rows||jj<0||jj>=cols)continue;
        result=std::min(result,std::max(0.0,dot(normals[i*cols+j],normals[ii*cols+jj])));found=true;}
    return found?result:1.0;
}

static double af_muscle_support(const std::vector<Vec>& points,int i,int j,int rows,int cols) {
    double result=INFINITY;const int offsets[4][2]={{-1,0},{1,0},{0,-1},{0,1}};
    for(auto& offset:offsets){int ii=i+offset[0],jj=j+offset[1];if(ii<0||ii>=rows||jj<0||jj>=cols)continue;
        result=std::min(result,norm(sub(points[ii*cols+jj],points[i*cols+j])));}
    return std::isfinite(result)?result:0.0;
}

static double af_muscle_distributed_amount(const AfMuscleOutput& out,const std::vector<Vec>& normals,const AfMuscleInput& input,int i,int j) {
    double fade=out.length_weights.empty()?af_muscle_length_fade(j,out.cols,input.taper):out.length_weights[i*out.cols+j];
    double raw=input.amount*af_muscle_edge_alpha(i,j,out.rows,out.cols,input,&out)*fade;
    double stable=af_muscle_stability(normals,i,j,out.rows,out.cols);if(raw<=0.0||stable>=0.85)return std::max(0.0,raw);
    double radius=af_muscle_support(out.base,i,j,out.rows,out.cols);double limit=radius>1.0e-8?radius*2.5:0.0;
    return std::min(raw,limit)+(raw-std::min(raw,limit))*std::clamp(stable/0.85,0.0,1.0);
}

static void af_muscle_inflate_distributed(AfMuscleOutput& out,const AfMuscleInput& input) {
    auto normals=af_muscle_normals(out.base,out.rows,out.cols,true);out.inflated=out.base;
    for(int i=0;i<out.rows;++i)for(int j=0;j<out.cols;++j){int index=i*out.cols+j;
        double amount=af_muscle_distributed_amount(out,normals,input,i,j);
        if(amount>0.0)out.inflated[index]=add(out.base[index],mul(normals[index],input.inflation_flip?-amount:amount));}
}

static double af_muscle_falloff(double value,int mode) {
    double x=std::clamp(value,0.0,1.0);if(mode==1)return 1.0-x;
    if(mode==2){double smooth=x*x*(3.0-2.0*x);return 1.0-smooth;}
    return std::exp(-4.0*x*x);
}

static int af_muscle_closest(const std::vector<Vec>& points,Vec control) {
    int best=0;double distance=INFINITY;
    for(int i=0;i<int(points.size());++i){Vec delta=sub(points[i],control);double value=dot(delta,delta);
        if(value<distance){distance=value;best=i;}}
    return best;
}

static void af_muscle_control_point(AfMuscleOutput&,const AfMuscleInput&,Vec,Vec,Vec,int,int);

static void af_muscle_inflate_control(AfMuscleOutput& out,const AfMuscleInput& input) {
    auto normals=af_muscle_normals(out.base,out.rows,out.cols,false);Vec control=input.initialize_control?out.base[(out.rows/2)*out.cols+out.cols/2]:af_vec(input.control);
    Vec n0=normals[af_muscle_closest(out.base,control)];double sign=input.inflation_flip?-1.0:1.0;
    Vec center=sub(control,mul(n0,input.depth*sign));out.inflated=out.base;
    for(int i=0;i<out.rows;++i)for(int j=0;j<out.cols;++j)af_muscle_control_point(out,input,control,n0,center,i,j);
}

static void af_muscle_control_point(AfMuscleOutput& out,const AfMuscleInput& input,Vec control,Vec n0,Vec center,int i,int j) {
    int index=i*out.cols+j;double edge=af_muscle_edge_alpha(i,j,out.rows,out.cols,input,&out);Vec delta=sub(out.base[index],control);
    double ratio=edge>0.0?norm(delta)/input.radius:2.0;if(edge<=0.0||(input.falloff!=0&&ratio>1.0))return;
    double weight=af_muscle_falloff(ratio,input.falloff);if(weight<=1.0e-8)return;Vec direction=sub(out.base[index],center);
    direction=norm(direction)>1.0e-10?af_muscle_unit(direction):n0;out.inflated[index]=add(out.base[index],mul(direction,input.amount*weight*edge));
}

static void af_muscle_inflate(AfMuscleOutput& out,const AfMuscleInput& input) {
    out.inflated=out.base;if(!input.inflation_enabled||input.amount<=0.0)return;
    if(input.inflation_mode==1)af_muscle_inflate_distributed(out,input);else af_muscle_inflate_control(out,input);
}

