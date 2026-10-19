static Vec af_env_unit(Vec v) { double l=norm(v);return l>0?mul(v,1/l):Vec{0,0,0}; }

static Vec af_env_gradient(const std::vector<Vec>& v,int r,int c,int i,int j,int axis) {
    int a=axis?j:i,n=axis?c:r,lo=std::max(0,a-1),hi=std::min(n-1,a+1);
    int first=axis?i*c+lo:lo*c+j,last=axis?i*c+hi:hi*c+j;
    return mul(sub(v[last],v[first]),1.0/(hi-lo));
}

static std::vector<Vec> af_env_gaussian(const std::vector<Vec>& v,int r,int c,int axis,double sigma) {
    int radius=int(4*sigma+.5);std::vector<double> weights(2*radius+1);double total=0;
    for(int k=-radius;k<=radius;++k)total+=(weights[k+radius]=std::exp(-.5*k*k/(sigma*sigma)));
    std::vector<Vec> out(v.size(),Vec{0,0,0});
    for(int i=0;i<r;++i)for(int j=0;j<c;++j)for(int k=-radius;k<=radius;++k){
        int a=axis?i:std::clamp(i+k,0,r-1),b=axis?std::clamp(j+k,0,c-1):j;
        out[i*c+j]=add(out[i*c+j],mul(v[a*c+b],weights[k+radius]/total));}
    return out;
}

static std::vector<Vec> af_env_frames(const std::vector<Vec>& v,int r,int c,std::vector<double>& areas) {
    std::vector<Vec> out(v.size());areas.resize(v.size());
    for(int i=0;i<r;++i)for(int j=0;j<c;++j){int k=i*c+j;
        Vec value=cross(af_env_gradient(v,r,c,i,j,0),af_env_gradient(v,r,c,i,j,1));
        areas[k]=norm(value);out[k]=af_env_unit(value);
        int previous=j?k-1:(i?(i-1)*c:-1);
        if(previous>=0&&dot(out[k],out[previous])<0)out[k]=mul(out[k],-1);}
    return out;
}

static std::vector<Vec> af_env_directions(std::vector<Vec> normals,const std::vector<double>& areas,int r,int c,int mode) {
    if(mode==1)return af_env_gaussian(af_env_gaussian(normals,r,c,0,std::max(1.,r*.12)),r,c,1,std::max(1.,c*.065));
    if(mode!=2)return normals;
    std::vector<Vec> column(c,Vec{0,0,0});
    for(int i=0;i<r;++i)for(int j=0;j<c;++j)column[j]=add(column[j],mul(normals[i*c+j],areas[i*c+j]));
    for(auto& v:column)v=af_env_unit(v);
    column=af_env_gaussian(column,1,c,1,std::max(1.,c*.08));
    for(int i=0;i<r;++i)std::copy(column.begin(),column.end(),normals.begin()+i*c);
    return normals;
}

static double af_env_endpoint(double a,double b) {
    double s=(3*a-b)*.5;if(s*a<=0)return 0;
    return a*b<=0&&std::abs(s)>3*std::abs(a)?3*a:s;
}

static double af_env_pchip(const double* y,double u) {
    double s[5],t[6]={};for(int i=0;i<5;++i)s[i]=5*(y[i+1]-y[i]);
    for(int i=1;i<5;++i)if(s[i-1]*s[i]>0)t[i]=2/(1/s[i-1]+1/s[i]);
    t[0]=af_env_endpoint(s[0],s[1]);t[5]=af_env_endpoint(s[4],s[3]);
    double p=std::clamp(u*5,0.,5.);int k=std::min(int(p),4);double x=p-k;
    return (2*x*x*x-3*x*x+1)*y[k]+(x*x*x-2*x*x+x)*.2*t[k]
        +(-2*x*x*x+3*x*x)*y[k+1]+(x*x*x-x*x)*.2*t[k+1];
}

static double af_env_diagonal(const std::vector<Vec>& v) {
    Vec low=v[0],high=v[0];
    for(auto p:v){low={std::min(low.x,p.x),std::min(low.y,p.y),std::min(low.z,p.z)};
        high={std::max(high.x,p.x),std::max(high.y,p.y),std::max(high.z,p.z)};}
    return norm(sub(high,low));
}

static int af_env_profile(const std::vector<Vec>& base,int r,int c,const double* p,int mode,int sign,std::vector<Vec>& out) {
    double depth[6]={0,p[0],p[1],p[2],p[3],0},peak[6]={p[4],p[4],p[5],p[6],p[7],p[7]};
    std::vector<double> areas;auto normals=af_env_directions(af_env_frames(base,r,c,areas),areas,r,c,mode);
    double limit=1e-12*std::pow(af_env_diagonal(base),2);out=base;
    for(int i=1;i<r-1;++i)for(int j=1;j<c-1;++j){double u=double(j)/(c-1),v=double(i)/(r-1);
        double d=std::max(0.,af_env_pchip(depth,u)),q=af_env_pchip(peak,u),x=v<=q?v/q:(1-v)/(1-q);
        double h=d*std::pow(std::max(0.,x*(2-x)),p[8]);int k=i*c+j;if(h==0)continue;
        if(areas[k]<=limit||norm(normals[k])<=1e-12)return 2;
        out[k]=add(base[k],mul(af_env_unit(normals[k]),sign*h));}
    return 0;
}

