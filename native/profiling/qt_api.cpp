#include "qt_profile.h"
#include "qt_observers.h"
#include <QQuickWindow>
#include <QCoreApplication>
#include <cstring>

#ifdef _WIN32
#define PROFILE_API extern "C" __declspec(dllexport)
#else
#define PROFILE_API extern "C" __attribute__((visibility("default")))
#endif

namespace {
QPointer<QQuickWindow> observedWindow;
QList<QPointer<QObject>> observedRoots;
}

PROFILE_API void af_profile_initialize() { profileRuntime().initialize(); }
PROFILE_API void af_profile_shutdown() { profileRuntime().shutdown(); }
PROFILE_API qint64 af_profile_clock() { return profileClock(); }

PROFILE_API void af_profile_start() {
    auto* receiver=profileRuntime().receiver;
    QMetaObject::invokeMethod(receiver,[receiver] { receiver->begin(); },Qt::BlockingQueuedConnection);
    observeModels(observedWindow,receiver);
    for (auto root:observedRoots) observeModelRoot(root);
}

PROFILE_API void af_profile_stop() {
    QMetaObject::invokeMethod(QCoreApplication::instance(),[] { stopObservingModels(); });
    auto* receiver=profileRuntime().receiver;
    QMetaObject::invokeMethod(receiver,[receiver] { receiver->end(); },Qt::QueuedConnection);
}

PROFILE_API int af_profile_read(char* buffer,int size,int status) {
    const auto data=status?profileRuntime().receiver->status():profileRuntime().receiver->drain();
    if (data.size()>=size) return -1;
    std::memcpy(buffer,data.constData(),data.size()); buffer[data.size()]=0;
    return int(data.size());
}

PROFILE_API void af_profile_window(void* pointer) {
    auto* window=static_cast<QQuickWindow*>(pointer);
    observedWindow=window;
    observedRoots.clear();
    auto* receiver=profileRuntime().receiver;
    QObject::connect(window,&QQuickWindow::beforeFrameBegin,receiver,[receiver] {
        receiver->instant("frame","before_frame"); },Qt::DirectConnection);
    QObject::connect(window,&QQuickWindow::afterRendering,receiver,[receiver] {
        receiver->instant("frame","after_rendering"); },Qt::DirectConnection);
    QObject::connect(window,&QQuickWindow::frameSwapped,receiver,[receiver] {
        receiver->instant("frame","submitted"); },Qt::DirectConnection);
}

PROFILE_API void af_profile_root(void* pointer) {
    observedRoots.append(static_cast<QObject*>(pointer));
}
