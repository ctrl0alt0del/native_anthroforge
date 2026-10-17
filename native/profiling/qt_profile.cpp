#include "qt_profile.h"
#include <QQmlDebuggingEnabler>
#include <QJsonDocument>
#include <QJsonArray>
#include <QUuid>
#include <QQuickWindow>
#include <chrono>
#ifdef _WIN32
#include <windows.h>
#elif defined(__linux__)
#include <time.h>
#endif

static qint64 threadCpuClock() {
#ifdef _WIN32
    FILETIME created,ended,kernel,user;
    if (!GetThreadTimes(GetCurrentThread(),&created,&ended,&kernel,&user)) return 0;
    const auto k=(quint64(kernel.dwHighDateTime)<<32)|kernel.dwLowDateTime;
    const auto u=(quint64(user.dwHighDateTime)<<32)|user.dwLowDateTime;
    return qint64(k+u)*100;
#elif defined(__linux__)
    timespec time{}; clock_gettime(CLOCK_THREAD_CPUTIME_ID,&time);
    return qint64(time.tv_sec)*1000000000+time.tv_nsec;
#else
    return 0;
#endif
}

class MeasuredClient final : public QQmlProfilerClient {
public:
    MeasuredClient(QQmlDebugConnection* connection,ProfileReceiver* receiver,quint64 features):
        QQmlProfilerClient(connection,receiver,features),sink(receiver) {}
    void messageReceived(const QByteArray& message) override {
        if (!sink->active) { QQmlProfilerClient::messageReceived(message); return; }
        const auto start=profileClock(),cpu=threadCpuClock();
        QQmlProfilerClient::messageReceived(message);
        sink->decodeNs+=profileClock()-start;
        sink->decodeCpuNs+=threadCpuClock()-cpu;
    }
private:
    ProfileReceiver* sink;
};

qint64 profileClock() {
    return std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count();
}

ProfileReceiver::ProfileReceiver(QObject* parent): QQmlProfilerEventReceiver(parent) {}

void ProfileReceiver::setup(const QString& socket) {
    connection=new QQmlDebugConnection(this);
    const quint64 features=(1ULL<<ProfileJavaScript)|(1ULL<<ProfileBinding)|
        (1ULL<<ProfileHandlingSignal)|(1ULL<<ProfileCreating)|(1ULL<<ProfileSceneGraph);
    client=new MeasuredClient(connection,this,features);
    client->setFlushInterval(100);
    connect(connection,&QQmlDebugConnection::connected,this,[this] { connected=true; });
    connect(connection,&QQmlDebugConnection::disconnected,this,[this] { connected=false; });
    connect(client,&QQmlProfilerClient::traceStarted,this,[this](qint64 t) { synchronize(t); });
    connect(client,&QQmlProfilerClient::complete,this,&ProfileReceiver::completeCapture);
    connection->startLocalServer(socket);
}

void ProfileReceiver::begin() {
    if (!connected) { fail("Qt profiling connection is unavailable"); return; }
    client->clearAll();
    clear();
    requested=profileClock();
    finished=false;
    active=true;
    client->setRecording(true);
}

void ProfileReceiver::end() {
    client->setRecording(false);
}

void ProfileReceiver::close() {
    active=false;
    delete client; client=nullptr;
    delete connection; connection=nullptr;
}

void ProfileReceiver::synchronize(qint64 stamp) {
    const auto now=profileClock();
    offset=requested+(now-requested)/2-stamp;
    uncertainty=(now-requested)/2;
}

void ProfileReceiver::clear() {
    QMutexLocker lock(&mutex);
    types.clear(); ranges.clear(); queue.clear();
    bytes=0; received=0; dropped=0; typeBytes=0; encodeNs=0;
    decodeNs=0; decodeCpuNs=0; modelWatchSkipped=0;
    failure.clear();
}

void ProfileReceiver::fail(const QString& message) {
    { QMutexLocker lock(&mutex); failure=message; }
    active=false;
    if (client) client->setRecording(false);
    finished=true;
}

void ProfileReceiver::record(QJsonObject event) {
    const auto start=profileClock();
    QByteArray data=QJsonDocument(event).toJson(QJsonDocument::Compact)+'\n';
    QMutexLocker lock(&mutex);
    while (bytes+data.size()>16*1024*1024 && !queue.empty()) {
        bytes-=queue.front().size(); queue.pop_front(); ++dropped;
    }
    bytes+=data.size(); queue.push_back(std::move(data)); ++received;
    encodeNs+=profileClock()-start;
}

QByteArray ProfileReceiver::drain() {
    QMutexLocker lock(&mutex);
    QByteArray result;
    while (!queue.empty() && result.size()<256*1024) {
        result.append(queue.front()); bytes-=queue.front().size(); queue.pop_front();
    }
    return result;
}

QByteArray ProfileReceiver::status() {
    QMutexLocker lock(&mutex);
    QJsonObject data{{"connected",bool(connected)},{"active",bool(active)},
        {"finished",bool(finished)},{"dropped",qint64(dropped)},{"queued_bytes",qint64(bytes)},
        {"clock_uncertainty_ns",qint64(uncertainty)},{"encode_ns",encodeNs},
        {"decode_inclusive_ns",qint64(decodeNs)},{"decode_cpu_ns",qint64(decodeCpuNs)},
        {"model_watch_skipped",qint64(modelWatchSkipped)},
        {"services",QJsonArray::fromStringList(QQmlDebuggingEnabler::profilerServices())},
        {"failure",failure},{"types",qint64(types.size())},{"qt_version",qVersion()},
        {"graphics_api",int(QQuickWindow::graphicsApi())}};
    return QJsonDocument(data).toJson(QJsonDocument::Compact);
}

void ProfileRuntime::initialize() {
    if (receiver) return;
    receiver=new ProfileReceiver;
    receiver->moveToThread(&thread);
    QObject::connect(&thread,&QThread::finished,receiver,&QObject::deleteLater);
    thread.setObjectName("AnthroForge profiler"); thread.start();
    const auto socket="anthroforge-profile-"+QUuid::createUuid().toString(QUuid::Id128);
    QMetaObject::invokeMethod(receiver,[this,socket] { receiver->setup(socket); },Qt::BlockingQueuedConnection);
    QQmlDebuggingEnabler::setServices(QQmlDebuggingEnabler::profilerServices());
    QQmlDebuggingEnabler::enableDebugging(false);
    QQmlDebuggingEnabler::connectToLocalDebugger(socket);
}

void ProfileRuntime::shutdown() {
    if (!receiver) return;
    QMetaObject::invokeMethod(receiver,[this] { receiver->close(); },Qt::BlockingQueuedConnection);
    thread.quit(); thread.wait(); receiver=nullptr;
}

ProfileRuntime& profileRuntime() {
    static ProfileRuntime runtime;
    return runtime;
}
