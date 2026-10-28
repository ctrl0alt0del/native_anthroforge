#pragma once
// Blender's guarded allocator uses these two mutex functions on Windows.
// No pthread runtime or competing task pool is introduced.
#include <mutex>
using pthread_mutex_t=std::mutex;
#define PTHREAD_MUTEX_INITIALIZER {}
inline int pthread_mutex_lock(pthread_mutex_t *mutex) { mutex->lock(); return 0; }
inline int pthread_mutex_unlock(pthread_mutex_t *mutex) { mutex->unlock(); return 0; }
struct pthread_rwlock_t;
struct pthread_cond_t;
