#include "process_windows.hpp"
#ifdef _WIN32
#include "mesh_internal.hpp"
#include <chrono>
namespace af::process {
void require(bool valid,const char* operation) {
    if(!valid) throw std::runtime_error(std::string(operation)+" failed (Windows "+std::to_string(GetLastError())+").");
}
std::wstring wide(const char* text) {
    if(!text) throw std::runtime_error("Missing process argument.");
    const int count=MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,text,-1,nullptr,0);
    require(count>0,"Decode process argument"); std::wstring result(size_t(count),L'\0');
    require(MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,text,-1,result.data(),count)>0,"Decode process argument");
    result.pop_back(); return result;
}
HANDLE file(const wchar_t* name,DWORD access,DWORD creation) {
    SECURITY_ATTRIBUTES security{sizeof(SECURITY_ATTRIBUTES),nullptr,TRUE};
    const auto handle=CreateFileW(name,access,FILE_SHARE_READ|FILE_SHARE_WRITE,&security,creation,FILE_ATTRIBUTE_NORMAL,nullptr);
    require(handle!=INVALID_HANDLE_VALUE,"Open backend stream"); return handle;
}
Process::~Process() {
    if(!value) return;
    TerminateJobObject(job,1);
    WaitForSingleObject(value,INFINITE);
}
Job::Job():Handle(CreateJobObjectW(nullptr,nullptr)) {
    require(value!=nullptr,"Create backend job");
}
Job::~Job() {
    if(!value) return;
    TerminateJobObject(value,1);
    JOBOBJECT_BASIC_ACCOUNTING_INFORMATION state{};
    while(QueryInformationJobObject(value,JobObjectBasicAccountingInformation,&state,sizeof(state),nullptr)) {
        if(!state.ActiveProcesses) break;
        Sleep(1);
    }
}
void limits(HANDLE job,uint64_t memory) {
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION info{};
    info.BasicLimitInformation.LimitFlags=JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE|JOB_OBJECT_LIMIT_JOB_MEMORY;
    info.JobMemoryLimit=SIZE_T(memory);
    require(SetInformationJobObject(job,JobObjectExtendedLimitInformation,&info,sizeof(info))!=0,"Set backend limits");
}
Startup::Startup(HANDLE log,HANDLE input,HANDLE job):inherited{log,input},assigned_job(job) {
    SIZE_T bytes=0; InitializeProcThreadAttributeList(nullptr,2,0,&bytes); storage.resize(bytes);
    auto list=reinterpret_cast<LPPROC_THREAD_ATTRIBUTE_LIST>(storage.data());
    require(InitializeProcThreadAttributeList(list,2,0,&bytes)!=0,"Initialize process attributes");
    info.lpAttributeList=list; info.StartupInfo.cb=sizeof(info);
    info.StartupInfo.dwFlags=STARTF_USESTDHANDLES;
    info.StartupInfo.hStdOutput=log; info.StartupInfo.hStdError=log; info.StartupInfo.hStdInput=input;
    try { attribute(PROC_THREAD_ATTRIBUTE_HANDLE_LIST,inherited,sizeof(inherited));
        attribute(PROC_THREAD_ATTRIBUTE_JOB_LIST,&assigned_job,sizeof(assigned_job)); }
    catch(...) { DeleteProcThreadAttributeList(list); info.lpAttributeList=nullptr; throw; }
}
void Startup::attribute(DWORD_PTR key,void* data,SIZE_T bytes) {
    require(UpdateProcThreadAttribute(info.lpAttributeList,0,key,data,bytes,nullptr,nullptr)!=0,"Set process attribute");
}
void spawn(const std::wstring& executable,std::wstring command,const std::wstring& directory,
           Startup& startup,Handle& process) {
    PROCESS_INFORMATION info{};
    const DWORD flags=CREATE_NO_WINDOW|EXTENDED_STARTUPINFO_PRESENT;
    require(CreateProcessW(executable.c_str(),command.data(),nullptr,nullptr,TRUE,flags,nullptr,
        directory.c_str(),&startup.info.StartupInfo,&info)!=0,"Start backend");
    process.value=info.hProcess; Handle thread(info.hThread);
}
uint32_t wait(HANDLE process,HANDLE log,uint64_t milliseconds,uint64_t log_limit,uint64_t cancel) {
    const auto start=std::chrono::steady_clock::now();
    while(true) {
        check_cancel(cancel); LARGE_INTEGER size{}; require(GetFileSizeEx(log,&size)!=0,"Read backend log size");
        if(uint64_t(size.QuadPart)>log_limit) throw std::runtime_error("Backend log limit exceeded.");
        if(std::chrono::steady_clock::now()-start>std::chrono::milliseconds(milliseconds))
            throw std::runtime_error("Backend execution timed out.");
        const auto state=WaitForSingleObject(process,25);
        require(state!=WAIT_FAILED,"Wait for backend"); if(state==WAIT_OBJECT_0) break;
    }
    DWORD code=0; require(GetExitCodeProcess(process,&code)!=0,"Read backend exit code"); return code;
}
}
#endif
