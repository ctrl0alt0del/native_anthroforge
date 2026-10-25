import QtQuick
import QtQuick.Controls

Menu {
    id: menu
    objectName: "menu" + title
    implicitWidth: 264
    onAboutToShow: fitWidth()
    function fitWidth() {
        let required=264;
        for(let i=0;i<count;++i) { const item=itemAt(i); if(item && item.visible) required=Math.max(required,item.implicitWidth+2*padding); }
        implicitWidth=Math.min(required,Math.max(264,Overlay.overlay.width-2*Theme.gap));
    }
    padding: 4
    margins: Theme.gap
    delegate: UiMenuItem {}
    background: Rectangle { color: Theme.panel; border.color: Theme.border; radius: Theme.radius + 2 }
}
