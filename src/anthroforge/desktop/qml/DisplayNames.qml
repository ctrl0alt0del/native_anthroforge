pragma Singleton
import QtQuick

QtObject {
    readonly property var labels: ({
        SCP:"Structural primitive", TISSUE:"Tissue", CURVE:"Curve", FIBER:"Fiber",
        SURFACE:"Surface", MEMBRANE:"Membrane", IMAGE:"Reference image", POINT:"Point", ANCHOR:"Anchor",
        LOFT:"Curve loft", BODY:"Curve body", IMPORTED:"Imported mesh", SEGMENT_CHAIN:"Segment chain",
        CTRL_POINT:"Control point", DISTRIBUTED:"Distributed", SECTION_PROFILE:"Section profile",
        NORMAL:"Surface normals", PROFILE:"Curve profile", RADIAL:"Radial",
        BEZIER:"Bézier", POLYLINE:"Polyline", ROUTED:"Routed", PARAMETRIC:"Parametric",
        INHERIT:"Inherit", ON_RELEASE:"On release", STATIC_PBD:"Static PBD",
        AUTO:"Automatic", B_SPLINE:"B-spline", BSPLINE:"B-spline", CATMULL_ROM:"Catmull–Rom",
        INT:"Integer", FLOAT:"Real number", BOOL:"Boolean",
        QUADWILD:"QuadWild · muscle flow", INSTANT:"Instant Meshes",
        LE:"Linear elasticity", FAST:"Reduced ARAP", MUSCLE_PROXIMITY:"Muscle proximity"
    })
    function label(code) {
        if(labels[code]) return labels[code];
        const text=String(code || "").replace(/_/g," ").toLowerCase();
        return text.charAt(0).toUpperCase()+text.slice(1);
    }
}
