#include "qt_profile.h"
#include <QUrl>
#include <QJsonArray>

void ProfileReceiver::addEventType(const QQmlProfilerEventType& type) {
    const auto size=256+2*(type.data().size()+type.location().filename().size());
    if (typeBytes+size>4*1024*1024) { fail("Qt event metadata exceeded budget"); return; }
    QMutexLocker lock(&mutex);
    typeBytes+=size;
    types.append(type);
}

QJsonObject ProfileReceiver::describe(const QQmlProfilerEventType& type) const {
    const auto location=type.location();
    static const char* categories[]={"painting","compiling","creating","binding","signal","javascript"};
    const int range=int(type.rangeType());
    const bool isRange=range>=0 && range<6;
    const QString file=QUrl(location.filename()).fileName();
    const QString category=file=="ProfileStatus.qml"?"profiler_ui":isRange?categories[range]:"scenegraph";
    return {{"cat","qml."+category},{"name",category+":"+file+":"+QString::number(location.line())},
        {"pid",1},{"tid",isRange?-1:-2},
        {"args",QJsonObject{{"file",file},{"line",location.line()},{"column",location.column()},
            {"detail",type.detailType()}}}};
}

void ProfileReceiver::rangeEvent(const QQmlProfilerEvent& event) {
    if (event.rangeStage()==RangeStart) {
        if (ranges.size()<4096) ranges.append({event.timestamp(),event.typeIndex()});
        else fail("Qt nesting exceeded budget");
        return;
    }
    if (event.rangeStage()!=RangeEnd || ranges.isEmpty()) return;
    const auto range=ranges.takeLast();
    auto data=describe(types[range.type]);
    data.insert("ph","X"); data.insert("ts",double(range.start+offset)/1000);
    data.insert("dur",double(event.timestamp()-range.start)/1000);
    record(data);
}

void ProfileReceiver::addEvent(const QQmlProfilerEvent& event) {
    if (!active || event.typeIndex()<0 || event.typeIndex()>=types.size()) return;
    const auto& type=types[event.typeIndex()];
    if (type.rangeType()<MaximumRangeType) { rangeEvent(event); return; }
    auto data=describe(type);
    QJsonArray values;
    for (int i=0;i<8;++i) values.append(event.number<qint64>(i));
    auto args=data["args"].toObject(); args.insert("qt_values",values); data.insert("args",args);
    data.insert("ph","i"); data.insert("s","t");
    data.insert("ts",double(event.timestamp()+offset)/1000);
    record(data);
}

void ProfileReceiver::instant(const char* category,const char* name,QJsonObject args) {
    if (!active) return;
    record({{"cat",category},{"name",name},{"ph","i"},{"s","t"},{"pid",1},
        {"tid",qint64(quintptr(QThread::currentThreadId()))},
        {"ts",double(profileClock())/1000},{"args",args}});
}

void ProfileReceiver::completeCapture() {
    while (!ranges.isEmpty()) {
        const auto range=ranges.takeLast();
        auto data=describe(types[range.type]);
        auto args=data["args"].toObject(); args.insert("truncated_end",true);
        const double start=double(range.start+offset)/1000;
        data.insert("args",args); data.insert("ph","X"); data.insert("ts",start);
        data.insert("dur",qMax(0.0,double(profileClock())/1000-start));
        record(data);
    }
    finished=true; active=false;
}
