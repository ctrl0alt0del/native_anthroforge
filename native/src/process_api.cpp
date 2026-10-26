#include "anthroforge/process.h"
#include "mesh_internal.hpp"
#include "process_windows.hpp"
#ifdef _WIN32
static uint32_t execute(const char* executable,const char* command,const char* directory,const char* path,
                        uint64_t memory,uint64_t milliseconds,uint64_t log_limit,uint64_t cancel) {
    using namespace af::process;
    af::check_cancel(cancel); Job job;
    limits(job.value,memory); Handle log(file(wide(path).c_str(),GENERIC_WRITE|GENERIC_READ,CREATE_ALWAYS));
    Handle input(file(L"NUL",GENERIC_READ,OPEN_EXISTING)); Startup startup(log.value,input.value,job.value);
    Process process(job.value); spawn(wide(executable),wide(command),wide(directory),startup,process);
    return wait(process.value,log.value,milliseconds,log_limit,cancel);
}
#endif
int af_process_run(const char* executable,const char* command,const char* directory,const char* log,
    uint64_t memory,uint64_t milliseconds,uint64_t log_limit,uint64_t cancel,uint32_t* exit_code) {
    try {
        if(!exit_code||!memory||!milliseconds||milliseconds>86400000||!log_limit)
            throw std::runtime_error("Invalid backend execution limits.");
#ifdef _WIN32
        *exit_code=execute(executable,command,directory,log,memory,milliseconds,log_limit,cancel); return 0;
#else
        (void)executable; (void)command; (void)directory; (void)log; (void)cancel;
        throw std::runtime_error("This external backend runner is qualified only on Windows.");
#endif
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
