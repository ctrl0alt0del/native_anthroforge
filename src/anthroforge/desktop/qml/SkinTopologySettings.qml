import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: editor
    required property var settings
    signal edited(string key, var value)
    Layout.fillWidth:true
    function component(key,index,value) {
        const vector=editor.settings[key].slice(); vector[index]=value;
        editor.edited(key,vector);
    }
    Label { text:"Topology"; color:Theme.text; font.bold:true; Layout.topMargin:Theme.gap }
    UiCombo {
        objectName:"skinBackend"; Layout.fillWidth:true; textRole:"label"; valueRole:"id"
        model:[{id:"QUADWILD",label:"QuadWild · Muscle FLOW + Paths"},{id:"INSTANT",label:"Instant Meshes"}]
        currentIndex:indexOfValue(editor.settings?.backend || "QUADWILD")
        hint:"Algorithm used to create the skin's quad mesh."
        onActivated:editor.edited("backend",currentValue)
    }
    NumericSetting { objectName:"skinQuadCount"; label:"Target quads"; minimum:1000; maximum:500000; decimals:0; value:editor.settings?.target_quads || 8100; onEdited:value=>editor.edited("target_quads",value) }
    Label { text:"Refinement"; color:Theme.muted }
    UiCombo {
        objectName:"skinRefinement"; Layout.fillWidth:true; enumLabels:true; model:["NONE","MUSCLE_PROXIMITY"]
        currentIndex:model.indexOf(editor.settings?.refinement)
        hint:"Add mesh detail near muscles."
        onActivated:editor.edited("refinement",currentText)
    }
    Label { text:"Symmetry"; color:Theme.muted }
    UiCombo {
        objectName:"skinSymmetry"; Layout.fillWidth:true; enumLabels:true; model:["NONE","X","Y","Z","CUSTOM"]
        currentIndex:model.indexOf(editor.settings?.symmetry)
        hint:"Symmetry plane for quad topology."
        onActivated:editor.edited("symmetry",currentText)
    }
    Repeater {
        model: editor.settings?.symmetry === "CUSTOM" ? ["plane_origin","plane_normal"] : []
        ColumnLayout {
            id: vector
            required property string modelData
            Layout.fillWidth:true
            Label { text:vector.modelData==="plane_origin" ? "Plane origin · m" : "Plane normal"; color:Theme.muted }
            Repeater {
                model:["X","Y","Z"]
                NumericSetting {
                    required property int index
                    required property string modelData
                    objectName:"skin_"+vector.modelData+modelData; label:modelData
                    minimum:-1000000; maximum:1000000
                    value:editor.settings?.[vector.modelData]?.[index] || 0
                    onEdited:value=>editor.component(vector.modelData,index,value)
                }
            }
        }
    }
}
