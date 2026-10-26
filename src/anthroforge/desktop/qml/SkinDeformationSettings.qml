import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: editor
    required property var settings
    signal edited(string key, var value)
    Layout.fillWidth: true
    Label { text:"Deformation"; color:Theme.text; font.bold:true; Layout.topMargin:Theme.gap }
    UiCombo {
        objectName:"skinDeformation"; Layout.fillWidth:true
        textRole:"label"; valueRole:"id"
        model:[{id:"LE",label:"Linear elasticity"},{id:"FAST",label:"FAST · reduced ARAP"}]
        currentIndex:indexOfValue(editor.settings?.method || "LE")
        hint:"How the final skin follows anatomy after its reference has been built."
        onActivated:editor.edited("method",currentValue)
    }
    NumericSetting {
        objectName:"skinProxyResolution"; label:"Proxy resolution"
        minimum:8; maximum:256; decimals:0; value:editor.settings?.proxy_resolution || 48
        hint:"Resolution of the internal volume used to deform the skin. Changing it requires rebuilding the reference."
        onEdited:value=>editor.edited("proxy_resolution",value)
    }
    NumericSetting {
        objectName:"skinConstraintStrength"; label:"Constraint strength"
        minimum:0.001; maximum:1000000; value:editor.settings?.constraint_strength || 100
        hint:"How strongly the internal volume follows its anatomical targets."
        onEdited:value=>editor.edited("constraint_strength",value)
    }
    NumericSetting {
        objectName:"skinFastHandles"; label:"FAST handles"
        minimum:5; maximum:1024; decimals:0; value:editor.settings?.fast_handles || 128
        visible:editor.settings?.method === "FAST"
        hint:"Number of reduced deformation handles. More handles allow finer movement at greater calculation cost."
        onEdited:value=>editor.edited("fast_handles",value)
    }
}
