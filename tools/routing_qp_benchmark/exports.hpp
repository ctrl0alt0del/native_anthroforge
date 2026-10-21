#if defined(_WIN32)
#define AF_LAB_EXPORT extern "C" __declspec(dllexport)
#else
#define AF_LAB_EXPORT extern "C" __attribute__((visibility("default")))
#endif
AF_LAB_EXPORT void af_route_lab_configure(int backend,int paired,int audit,double tolerance) {
    afbench::config={backend,paired,audit,0,tolerance}; afbench::records.clear();
}
AF_LAB_EXPORT const char* af_route_lab_records() { return afbench::csv(); }
