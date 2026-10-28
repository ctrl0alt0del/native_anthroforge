#include "process_windows.hpp"
#ifdef _WIN32
namespace af::process {
struct Processes {
    std::vector<HANDLE> handles;
    ~Processes() { for(auto handle:handles) CloseHandle(handle); }
};
static void capture(HANDLE job,Processes& processes) {
    std::vector<ULONG_PTR> storage(34);
    while(true) {
        auto* list=reinterpret_cast<JOBOBJECT_BASIC_PROCESS_ID_LIST*>(storage.data());
        const auto valid=QueryInformationJobObject(job,JobObjectBasicProcessIdList,list,DWORD(storage.size()*sizeof(ULONG_PTR)),nullptr);
        if(!valid&&GetLastError()==ERROR_MORE_DATA) { storage.resize(size_t(list->NumberOfAssignedProcesses)+2); continue; }
        if(!valid) return;
        for(DWORD i=0;i<list->NumberOfProcessIdsInList;++i)
            if(auto handle=OpenProcess(SYNCHRONIZE,FALSE,DWORD(list->ProcessIdList[i]))) processes.handles.push_back(handle);
        return;
    }
}
void stop(HANDLE job) {
    Processes processes; capture(job,processes);
    TerminateJobObject(job,1);
    for(auto handle:processes.handles) WaitForSingleObject(handle,INFINITE);
}
}
#endif
