#include "process_windows.hpp"
#ifdef _WIN32
#include <algorithm>
#include <array>
#include <cstring>
namespace af::process {
Log::Log(const std::wstring& path,uint64_t capacity)
    :output(file(path.c_str(),GENERIC_WRITE,CREATE_ALWAYS)),tail(size_t(capacity)) {
    SECURITY_ATTRIBUTES security{sizeof(SECURITY_ATTRIBUTES),nullptr,TRUE};
    require(CreatePipe(&reader.value,&writer.value,&security,65536)!=0,"Create backend log pipe");
    require(SetHandleInformation(reader.value,HANDLE_FLAG_INHERIT,0)!=0,"Protect backend log reader");
}
void Log::append(const char* bytes,size_t count) {
    received+=count;
    if(count>=tail.size()) { bytes+=count-tail.size(); count=tail.size(); next=0; }
    const auto first=std::min(count,tail.size()-next);
    std::memcpy(tail.data()+next,bytes,first);
    std::memcpy(tail.data(),bytes+first,count-first);
    next=(next+count)%tail.size(); used=std::min(tail.size(),used+count);
}
static DWORD available(HANDLE pipe) {
    DWORD count=0;
    if(PeekNamedPipe(pipe,nullptr,0,nullptr,&count,nullptr)) return count;
    require(GetLastError()==ERROR_BROKEN_PIPE,"Inspect backend log pipe"); return 0;
}
bool Log::drain() {
    std::array<char,65536> bytes{}; size_t remaining=262144;
    while(remaining) {
        const DWORD count=std::min<DWORD>(available(reader.value),DWORD(std::min(remaining,bytes.size())));
        if(!count) return false;
        DWORD read=0; require(ReadFile(reader.value,bytes.data(),count,&read,nullptr)!=0,"Read backend log");
        if(!read) return false;
        append(bytes.data(),read); remaining-=read;
    }
    return true;
}
static void write(HANDLE output,const char* bytes,size_t count) {
    while(count) {
        const DWORD portion=DWORD(std::min<size_t>(count,65536)); DWORD written=0;
        require(WriteFile(output,bytes,portion,&written,nullptr)!=0&&written>0,"Write backend log");
        count-=written; bytes+=written;
    }
}
void Log::flush() {
    while(drain()) {}
    if(received>used) {
        const auto message="[AnthroForge: discarded "+std::to_string(received-used)+" earlier log bytes; retained tail follows]\n";
        write(output.value,message.data(),message.size());
    }
    const auto start=used==tail.size()?next:0, first=std::min(used,tail.size()-start);
    write(output.value,tail.data()+start,first); write(output.value,tail.data(),used-first);
}
}
#endif
