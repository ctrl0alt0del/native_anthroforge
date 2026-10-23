import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    required property var curve
    readonly property var config: curve.engine_settings || {}
    readonly property var interval: config.interval || {}
    readonly property var variables: config.variables || []
    readonly property var resolutionReference: ({target:curve.id,path:["engine_settings","resolution"]})
    readonly property var resolutionState: workspace.shortcutPanel.propertyState(resolutionReference,workspace.state.revision)
    readonly property string samplingReason: workspace.authoring.samplingLockReason(curve.id,workspace.state.revision)
    title: "Parametric equations"
    visible: curve.engine === "PARAMETRIC"
    UiNotice { active: panel.visible; text: panel.curve.result?.status === "failed" && !panel.curve.result?.asset ? "Invalid Parametric curve · straight-line placeholder only; consumers require an accepted path" : "" }
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
    UiCombo { objectName: "parametricInterpolation"; Layout.fillWidth: true; model: ["POLYLINE","BEZIER"]; currentIndex: model.indexOf(panel.config.interpolation || "POLYLINE"); enabled: !panel.samplingReason; hint: panel.samplingReason; onActivated: panel.setting("interpolation",currentText) }
    NumericSetting { objectName: "parametricBezierResolution"; propertyReference: ({target:panel.curve.id,path:["engine_settings","bezier_resolution"]}); visible: panel.config.interpolation === "BEZIER"; label: "Bézier samples per segment"; decimals: 0; minimum: 1; maximum: 1024; hint: panel.samplingReason; value: panel.config.bezier_resolution || 24; onEdited: value => panel.setting("bezier_resolution",Math.round(value)) }
    NumericSetting { propertyReference: panel.resolutionReference; objectName: "parametricResolution"; label: "Generated points"; decimals: 0; minimum: panel.curve.closed ? 3 : 2; maximum: 1000000; value: panel.config.resolution || 64; hint: panel.resolutionState.reason || "Uniform parameter sampling; closed curves omit a duplicate seam endpoint"; onEdited: value => panel.setting("resolution",Math.round(value)) }
    Repeater {
        model: ["start","end"]
        ColumnLayout {
            required property string modelData
            Layout.fillWidth: true
            NumericSetting { propertyReference: ({target:panel.curve.id,path:["engine_settings","interval",modelData]}); label: modelData === "start" ? "t start" : "t end"; value: panel.interval[modelData] || 0; enabled: !panel.interval[modelData+"_expression"]; hint: enabled ? "" : "Controlled by the interval expression below"; onEdited: value => { const change={}; change[modelData]=value; panel.configure({interval:change}); } }
            UiField { Layout.fillWidth: true; placeholderText: "Optional "+modelData+" expression"; text: panel.interval[modelData+"_expression"] || ""; onEditingFinished: { const change={}; change[modelData+"_expression"]=text; panel.configure({interval:change}); } }
        }
    }
    RowLayout {
        Layout.fillWidth: true
        Label { text: "Variables"; color: Theme.text; Layout.fillWidth: true }
        UiButton { objectName: "addParametricVariable"; text: "+ Variable"; onClicked: { let i=1; while(panel.variables.some(v=>v.name==="v"+i)) ++i; workspace.run("curve.parametric.variable.add",{curve:panel.curve.id,name:"v"+i}); } }
    }
    ListView {
        objectName: "parametricVariables"; Layout.fillWidth: true; Layout.preferredHeight: Math.min(440,count*160)
        model: panel.variables; clip: true; spacing: 5; ScrollBar.vertical: ScrollBar {}
        delegate: ColumnLayout {
            required property var modelData
            width: ListView.view.width; height: 155
            RowLayout {
                Layout.fillWidth: true
                UiField { Layout.fillWidth: true; text: modelData.name; placeholderText: "Expression name"; onEditingFinished: panel.variable(modelData.id,{name:text}) }
                UiButton { text: "×"; hint: "Remove variable"; onClicked: workspace.run("curve.parametric.variable.remove",{curve:panel.curve.id,variable:modelData.id}) }
            }
            UiField { Layout.fillWidth: true; text: modelData.label || ""; placeholderText: "Display label (optional)"; onEditingFinished: panel.variable(modelData.id,{label:text}) }
            RowLayout {
                Layout.fillWidth: true
                UiCombo { objectName: "parametricVariableType"+modelData.id; model: ["REAL","INTEGER"]; currentIndex: model.indexOf(modelData.numeric_type); Layout.fillWidth: true; onActivated: { const changes={numeric_type:currentText}; if(currentText==="INTEGER" && modelData.numeric_type!=="INTEGER" && Number.isInteger(modelData.value)) changes.value=modelData.value; panel.variable(modelData.id,changes); } }
                UiCombo { model: ["SCALAR","LENGTH","ANGLE"]; currentIndex: model.indexOf(modelData.dimension); Layout.fillWidth: true; onActivated: panel.variable(modelData.id,{dimension:currentText}) }
            }
            RowLayout {
                Layout.fillWidth: true
                UiQuantityField { id: variableValue; objectName: "parametricVariable"+modelData.id; propertyReference: ({target:panel.curve.id,path:["engine_settings","variables","@"+modelData.id,"value"]}); Layout.fillWidth: true; canonicalValue: workspace.shortcutPanel.propertyText(propertyReference,workspace.state.revision); numericType: modelData.numeric_type; dimension: modelData.dimension; onCanonicalEdited: value => panel.variable(modelData.id,{value:value}) }
                Label { text: variableValue.unitLabel; color: Theme.muted; Layout.preferredWidth: 20 }
            }
        }
    }
}
