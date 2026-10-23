import QtQuick

UiNumberField {
    id: field
    property var canonicalValue: 0
    property string numericType: "REAL"
    property string dimension: "SCALAR"
    readonly property real factor: dimension === "LENGTH" ? workspace.state.unit_factor : dimension === "ANGLE" ? Math.PI/180 : 1
    readonly property string unitLabel: dimension === "LENGTH" ? workspace.state.display_units : dimension === "ANGLE" ? "°" : ""
    readonly property var quantities: workspace.shortcutPanel.quantityValues
    signal canonicalEdited(var value)
    exactText: numericType === "INTEGER"
    exactOffset: (start,steps) => quantities.offsetInteger(start,steps,dimension,workspace.state.display_units)
    value: canonicalValue === "" ? "" : exactText ? quantities.displayInteger(String(canonicalValue),dimension,workspace.state.display_units) : Number(canonicalValue)/factor
    decimals: exactText && dimension !== "ANGLE" ? 0 : 4
    onEdited: value => canonicalEdited(value*factor)
    onExactEdited: value => canonicalEdited({integer_text:value,dimension:field.dimension,display_units:workspace.state.display_units})
}
