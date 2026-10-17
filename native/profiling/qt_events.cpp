#include "qt_profile.h"
#include <QUrl>

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
    const QString category=range<6?categories[range]:"scenegraph";
    const QString file=QUrl(location.filename()).fileName();
    return {{"cat","qml."+category},{"name",category+":"+file+":"+QString::number(location.line())},
        {"pid",1},{"tid",range<6?"qml":"scenegraph"},
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
    data.insert("ph","i"); data.insert("s","t");
    data.insert("ts",double(event.timestamp()+offset)/1000);
    record(data);
}

void ProfileReceiver::instant(const char* category,const char* name,QJsonObject args) {
    if (!active) return;
    record({{"cat",category},{"name",name},{"ph","i"},{"s","t"},{"pid",1},
        {"tid",QString::number(quintptr(QThread::currentThreadId()))},
        {"ts",double(profileClock())/1000},{"args",args}});
}
