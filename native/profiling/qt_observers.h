#pragma once
#include "qt_profile.h"
#include <QPointer>
#include <QSet>

class ModelObserver final : public QObject {
    Q_OBJECT
public:
    ModelObserver(QObject* root,ProfileReceiver* receiver);
    void watch(QObject* object);
    bool eventFilter(QObject* watched,QEvent* event) override;
private slots:
    void changed();
private:
    ProfileReceiver* receiver;
    QSet<QObject*> watched;
    void connectSignals(QObject* object);
};

void observeModels(QObject* root,ProfileReceiver* receiver);
void stopObservingModels();
void observeModelRoot(QObject* root);
