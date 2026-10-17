#include "qt_profile.h"
#include <QGuiApplication>
#include <QInputEvent>

class ProfileApplication final : public QGuiApplication {
public:
    ProfileApplication(int& argc,char** argv): QGuiApplication(argc,argv) {}
    bool notify(QObject* receiver,QEvent* event) override;
};

static bool inputEvent(QEvent* event) {
    return event->type()==QEvent::MouseMove || event->type()==QEvent::MouseButtonPress ||
        event->type()==QEvent::MouseButtonRelease || event->type()==QEvent::KeyPress ||
        event->type()==QEvent::KeyRelease || event->type()==QEvent::Wheel;
}

bool ProfileApplication::notify(QObject* object,QEvent* event) {
    auto* sink=profileRuntime().receiver;
    if (!sink || !sink->active || !inputEvent(event)) return QGuiApplication::notify(object,event);
    const auto start=profileClock();
    const int type=int(event->type()),mods=int(static_cast<QInputEvent*>(event)->modifiers());
    const bool result=QGuiApplication::notify(object,event);
    sink->record({{"cat","input"},{"name","dispatch"},{"ph","X"},{"pid",1},
        {"tid",qint64(quintptr(QThread::currentThreadId()))},
        {"ts",double(start)/1000},{"dur",double(profileClock()-start)/1000},
        {"args",QJsonObject{{"type",type},{"modifiers",mods}}}});
    return result;
}

#ifdef _WIN32
extern "C" __declspec(dllexport) void* af_profile_application() {
#else
extern "C" __attribute__((visibility("default"))) void* af_profile_application() {
#endif
    static int argc=1;
    static char name[]="AnthroForge";
    static char* argv[]={name,nullptr};
    return new ProfileApplication(argc,argv);
}
