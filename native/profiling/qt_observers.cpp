#include "qt_observers.h"
#include <QChildEvent>
#include <QCoreApplication>
#include <QMetaMethod>
#include <QQmlContext>
#include <QQmlEngine>
#include <QTimer>

namespace { QPointer<ModelObserver> observer; }

ModelObserver::ModelObserver(QObject* root,ProfileReceiver* sink): QObject(root),receiver(sink) {
    QCoreApplication::instance()->installEventFilter(this);
    addRoot(root);
}

void ModelObserver::addRoot(QObject* root) {
    if (!root || roots.contains(root)) return;
    if (roots.size()>=16) { ++receiver->modelWatchSkipped; return; }
    roots.append(root); watch(root);
}

static bool modelSignal(const QMetaMethod& method) {
    const QList<QByteArray> names={"modelChanged","modelReset","rowsInserted","rowsRemoved","dataChanged"};
    return method.methodType()==QMetaMethod::Signal && names.contains(method.name());
}

static bool observable(QObject* object) {
    if (object->objectName()=="keyboardManager") return true;
    const auto* meta=object->metaObject();
    for (int i=0;i<meta->methodCount();++i) if (modelSignal(meta->method(i))) return true;
    return false;
}

void ModelObserver::watch(QObject* object) {
    if (watched.contains(object) || object==this) return;
    if (observable(object)) {
        if (watched.size()>=16384) { ++receiver->modelWatchSkipped; return; }
        watched.insert(object);
        connect(object,&QObject::destroyed,this,[this,object] { watched.remove(object); });
        connectSignals(object);
        if (object->objectName()=="keyboardManager")
            connect(object,SIGNAL(requested(QString)),this,SLOT(action(QString)),Qt::DirectConnection);
    }
    for (auto* child:object->children()) watch(child);
}

void ModelObserver::connectSignals(QObject* object) {
    const auto* meta=object->metaObject();
    const auto slot=metaObject()->method(metaObject()->indexOfSlot("changed()"));
    for (int i=0;i<meta->methodCount();++i) {
        const auto method=meta->method(i);
        if (modelSignal(method))
            QObject::connect(object,method,this,slot,Qt::DirectConnection);
    }
}

bool ModelObserver::contains(QObject* object) const {
    for (auto* item=object;item;item=item->parent()) {
        if (item==this) return false;
        if (roots.contains(item)) return true;
    }
    return false;
}

bool ModelObserver::eventFilter(QObject* object,QEvent* event) {
    if (event->type()==QEvent::ChildAdded && contains(object)) {
        if (pending>=4096) { ++receiver->modelWatchSkipped; return false; }
        ++pending;
        QPointer<QObject> child=static_cast<QChildEvent*>(event)->child();
        QTimer::singleShot(0,this,[this,child] { --pending; if (child) watch(child); });
    }
    return false;
}

void ModelObserver::changed() {
    auto* object=sender();
    if (!object || !receiver->active) return;
    const auto signal=object->metaObject()->method(senderSignalIndex()).name();
    auto* context=QQmlEngine::contextForObject(object);
    receiver->instant("model",signal.constData(),{{"object",object->objectName()},
        {"class",object->metaObject()->className()},
        {"source",context?context->baseUrl().fileName():QString()}});
}

void ModelObserver::action(const QString& name) {
    receiver->instant("input.action",name.toUtf8().constData());
}

void observeModels(QObject* root,ProfileReceiver* receiver) {
    stopObservingModels();
    if (root) observer=new ModelObserver(root,receiver);
}

void stopObservingModels() { delete observer; }

void observeModelRoot(QObject* root) { if (observer && root) observer->addRoot(root); }
