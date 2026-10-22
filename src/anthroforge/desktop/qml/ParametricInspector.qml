import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    required property var curve
    property bool topologyLocked: false
    readonly property var config: curve.engine_settings || {}
    readonly property var interval: config.interval || {}
    readonly property var variables: config.variables || []
    readonly property bool joined: (curve.points || []).some(p => !!p.junction)
    title: "Parametric equations"
    visible: curve.engine === "PARAMETRIC"
    function configure(changes) { workspace.run("curve.parametric.configure",{curve:curve.id,changes:changes}); }
    function setting(name,value) { const changes={}; changes[name]=value; configure(changes); }
    function variable(id,changes) { workspace.run("curve.parametric.variable.update",{curve:curve.id,variable:id,changes:changes}); }
    Repeater {
        model: ["x","y","z"]
        RowLayout {
            required property string modelData
            Layout.fillWidth: true
            Label { text: modelData.toUpperCase()+"(t)"; color: Theme.muted; Layout.preferredWidth: 32 }
            UiField { objectName: "parametricExpression"+modelData; Layout.fillWidth: true; text: panel.config[modelData] || ""; onEditingFinished: panel.setting(modelData,text) }
        }
    }
    Label { text: "XYZ produce metres · t is dimensionless · m and rad are unit constants"; color: Theme.muted; wrapMode: Text.Wrap; Layout.fillWidth: true; font.pixelSize: 10 }
    NumericSetting { objectName: "parametricResolution"; label: "Generated points"; decimals: 0; minimum: panel.curve.closed ? 3 : 2; maximum: 1000000; value: panel.config.resolution || 64; enabled: !panel.topologyLocked && !panel.joined; hint: panel.joined ? "Resolution is locked while this curve has a junction" : panel.topologyLocked ? "Resolution is locked by incoming attachments" : "Uniform parameter sampling; closed curves omit a duplicate seam endpoint"; onEdited: value => panel.setting("resolution",Math.round(value)) }
    Repeater {
        model: ["start","end"]
        ColumnLayout {
            required property string modelData
            Layout.fillWidth: true
            NumericSetting { label: modelData === "start" ? "t start" : "t end"; value: panel.interval[modelData] || 0; enabled: !panel.interval[modelData+"_expression"]; hint: enabled ? "" : "Controlled by the interval expression below"; onEdited: value => { const change={}; change[modelData]=value; panel.configure({interval:change}); } }
            UiField { Layout.fillWidth: true; placeholderText: "Optional "+modelData+" expression"; text: panel.interval[modelData+"_expression"] || ""; onEditingFinished: { const change={}; change[modelData+"_expression"]=text; panel.configure({interval:change}); } }
        }
    }
    RowLayout {
        Layout.fillWidth: true
        Label { text: "Variables"; color: Theme.text; Layout.fillWidth: true }
        UiButton { objectName: "addParametricVariable"; text: "+ Variable"; onClicked: { let i=1; while(panel.variables.some(v=>v.name==="v"+i)) ++i; workspace.run("curve.parametric.variable.add",{curve:panel.curve.id,name:"v"+i}); } }
    }
    ListView {
        objectName: "parametricVariables"; Layout.fillWidth: true; Layout.preferredHeight: Math.min(330,count*125)
        model: panel.variables; clip: true; spacing: 5; ScrollBar.vertical: ScrollBar {}
        delegate: ColumnLayout {
            required property var modelData
            width: ListView.view.width; height: 120
            RowLayout {
                Layout.fillWidth: true
                UiField { Layout.fillWidth: true; text: modelData.name; placeholderText: "Expression name"; onEditingFinished: panel.variable(modelData.id,{name:text}) }
                UiButton { text: "×"; hint: "Remove variable"; onClicked: workspace.run("curve.parametric.variable.remove",{curve:panel.curve.id,variable:modelData.id}) }
            }
            UiField { Layout.fillWidth: true; text: modelData.label || ""; placeholderText: "Display label (optional)"; onEditingFinished: panel.variable(modelData.id,{label:text}) }
            RowLayout {
                Layout.fillWidth: true
                UiCombo { model: ["REAL","INTEGER"]; currentIndex: model.indexOf(modelData.numeric_type); Layout.fillWidth: true; onActivated: panel.variable(modelData.id,{numeric_type:currentText}) }
                UiCombo { model: ["SCALAR","LENGTH","ANGLE"]; currentIndex: model.indexOf(modelData.dimension); Layout.fillWidth: true; onActivated: panel.variable(modelData.id,{dimension:currentText}) }
                UiNumberField { Layout.preferredWidth: 95; value: modelData.value; decimals: modelData.numeric_type === "INTEGER" ? 0 : 4; onEdited: value => panel.variable(modelData.id,{value:value}) }
            }
        }
    }
}
