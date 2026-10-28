#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
/* UTF-8 paths/command; limits are bytes/milliseconds. Executes on the caller's worker. */
AF_API int af_process_run(const char* executable,const char* command,const char* directory,
    const char* log,uint64_t memory,uint64_t milliseconds,uint64_t log_limit,uint64_t cancel,uint32_t* exit_code);
#ifdef __cplusplus
}
#endif
