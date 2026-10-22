import QtQuick

UiNumberField {
    id: field
    property real canonicalValue: 0
    property string numericType: "REAL"
    property string dimension: "SCALAR"
    readonly property real factor: dimension === "LENGTH" ? workspace.state.unit_factor : dimension === "ANGLE" ? Math.PI/180 : 1
    readonly property string unitLabel: dimension === "LENGTH" ? workspace.state.display_units : dimension === "ANGLE" ? "°" : ""
    signal canonicalEdited(real value)
    value: canonicalValue/factor
    decimals: numericType === "INTEGER" ? 0 : 4
    onEdited: value => canonicalEdited(value*factor)
}
