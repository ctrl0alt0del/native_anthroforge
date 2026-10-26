#pragma once
#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <string>
#include <vector>
#include <stdexcept>
namespace af::process {
void require(bool valid,const char* operation);
std::wstring wide(const char* text);
struct Handle {
    HANDLE value=nullptr;
    explicit Handle(HANDLE source=nullptr):value(source) {}
    ~Handle() { if(value&&value!=INVALID_HANDLE_VALUE) CloseHandle(value); }
    Handle(const Handle&)=delete;
    Handle& operator=(const Handle&)=delete;
};
struct Log {
    Handle output, reader, writer;
    std::vector<char> tail;
    uint64_t received=0;
    size_t next=0, used=0;
    Log(const std::wstring& path,uint64_t capacity);
    void append(const char* bytes,size_t count);
    bool drain();
    void flush();
};
struct Job : Handle {
    Job();
    ~Job();
};
void stop(HANDLE job);
struct Process : Handle {
    HANDLE job;
    explicit Process(HANDLE owner):job(owner) {}
    ~Process();
};
struct Startup {
    STARTUPINFOEXW info{};
    std::vector<unsigned char> storage;
    HANDLE inherited[2];
    HANDLE assigned_job;
    Startup(HANDLE log,HANDLE input,HANDLE job);
    ~Startup() { if(info.lpAttributeList) DeleteProcThreadAttributeList(info.lpAttributeList); }
    void attribute(DWORD_PTR key,void* data,SIZE_T bytes);
};
void limits(HANDLE job,uint64_t memory);
HANDLE file(const wchar_t* name,DWORD access,DWORD creation);
void spawn(const std::wstring& executable,std::wstring command,const std::wstring& directory,
    Startup& startup,Handle& process);
uint32_t wait(HANDLE process,Log& log,uint64_t milliseconds,uint64_t cancel);
}
#endif
