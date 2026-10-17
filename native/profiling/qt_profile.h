#pragma once
#include <QtQmlDebug/private/qqmlprofilerclient_p.h>
#include <QtQmlDebug/private/qqmldebugconnection_p.h>
#include <QJsonObject>
#include <QMutex>
#include <QThread>
#include <atomic>
#include <deque>

qint64 profileClock();

class ProfileReceiver final : public QQmlProfilerEventReceiver {
    Q_OBJECT
public:
    explicit ProfileReceiver(QObject* parent=nullptr);
    qsizetype numLoadedEventTypes() const override { return types.size(); }
    qsizetype numLoadedEvents() const override { return received; }
    void addEventType(const QQmlProfilerEventType& type) override;
    void addEvent(const QQmlProfilerEvent& event) override;
    void clear() override;
    void setup(const QString& socket);
    void begin();
    void end();
    void close();
    void synchronize(qint64 stamp);
    QByteArray drain();
    QByteArray status();
    void record(QJsonObject event);
    void instant(const char* category,const char* name,QJsonObject args={});
    std::atomic<bool> active{false};
    std::atomic<bool> finished{true};
    std::atomic<bool> connected{false};
    std::atomic<qint64> offset{0};
    std::atomic<qint64> uncertainty{0};
private:
    struct Range { qint64 start; int type; };
    QQmlDebugConnection* connection=nullptr;
    QQmlProfilerClient* client=nullptr;
    QList<QQmlProfilerEventType> types;
    QList<Range> ranges;
    QMutex mutex;
    std::deque<QByteArray> queue;
    qsizetype bytes=0, received=0, dropped=0, typeBytes=0;
    qint64 requested=0, encodeNs=0;
    QString failure;
    void rangeEvent(const QQmlProfilerEvent& event);
    QJsonObject describe(const QQmlProfilerEventType& type) const;
    void fail(const QString& message);
};

struct ProfileRuntime {
    QThread thread;
    ProfileReceiver* receiver=nullptr;
    void initialize();
    void shutdown();
};
ProfileRuntime& profileRuntime();
