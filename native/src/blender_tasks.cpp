// Run Blender callbacks on the existing coordinator worker, without another pool.
#include "BLI_task.h"
#include "BLI_mempool.h"
#include <stdexcept>
static void independent(const TaskParallelSettings *settings) {
    if(settings->userdata_chunk_size||settings->func_init||settings->func_reduce||settings->func_free)
        throw std::runtime_error("BMesh task adapter supports independent geometry callbacks only.");
}
void BLI_task_parallel_mempool(BLI_mempool *pool,void *data,TaskParallelMempoolFunc callback,const TaskParallelSettings *settings) {
    independent(settings);
    BLI_mempool_iter iter; BLI_mempool_iternew(pool,&iter); TaskParallelTLS tls{};
    while(void *item=BLI_mempool_iterstep(&iter)) callback(data,static_cast<MempoolIterData *>(item),&tls);
}
void BLI_task_parallel_range(int start,int end,void *data,TaskParallelRangeFunc callback,const TaskParallelSettings *settings) {
    independent(settings); TaskParallelTLS tls{};
    for(int i=start;i<end;++i) callback(data,i,&tls);
}
