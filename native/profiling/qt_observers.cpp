#include "qt_observers.h"
#include <QChildEvent>
#include <QMetaMethod>
#include <QQmlContext>
#include <QQmlEngine>
#include <QTimer>

namespace { QPointer<ModelObserver> observer; }

ModelObserver::ModelObserver(QObject* root,ProfileReceiver* sink): QObject(root),receiver(sink) {
    watch(root);
}

void ModelObserver::watch(QObject* object) {
    if (watched.contains(object) || object==this || watched.size()>=16384) return;
    watched.insert(object);
    object->installEventFilter(this);
    connect(object,&QObject::destroyed,this,[this,object] { watched.remove(object); });
    connectSignals(object);
    for (auto* child:object->children()) watch(child);
}

void ModelObserver::connectSignals(QObject* object) {
    const auto* meta=object->metaObject();
    const auto slot=metaObject()->method(metaObject()->indexOfSlot("changed()"));
    const QList<QByteArray> names={"modelChanged","modelReset","rowsInserted","rowsRemoved","dataChanged"};
    for (int i=0;i<meta->methodCount();++i) {
        const auto method=meta->method(i);
        if (method.methodType()==QMetaMethod::Signal && names.contains(method.name()))
            QObject::connect(object,method,this,slot,Qt::DirectConnection);
    }
}

bool ModelObserver::eventFilter(QObject*,QEvent* event) {
    if (event->type()==QEvent::ChildAdded) {
        QPointer<QObject> child=static_cast<QChildEvent*>(event)->child();
        QTimer::singleShot(0,this,[this,child] { if (child) watch(child); });
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

void observeModels(QObject* root,ProfileReceiver* receiver) {
    stopObservingModels();
    if (root) observer=new ModelObserver(root,receiver);
}

void stopObservingModels() { delete observer; }
