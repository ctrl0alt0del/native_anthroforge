import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick3D
import QtQuick3D.Helpers
import AnthroForge.Native 1.0

Item {
    id: viewport
    signal importRequested()
    property bool gridVisible: true
    property bool xray: false
    property string viewName: "User view"
    property string toolMode: "Move"
    property string anchorMode: ""
    property bool orthographic: false
    property real distance: 4
    property int depthIndex: 0
    property point pointerPosition: Qt.point(-1, -1)
    property point previousPointer: Qt.point(-2, -2)
    property bool cameraDirty: true
    property bool restoringCamera: false
    readonly property var selected: authoring.transformData
    readonly property real gizmoSize: distance * 0.16

    function inspectScene(): string {
        let vertices = 0, finite = true;
        for (let i=0;i<meshRepeater.count;i++) {
            const node=meshRepeater.objectAt(i), model=node.meshNode, p=model.scenePosition;
            vertices += model.geometry.vertexCount;
            finite = finite && isFinite(p.x) && isFinite(p.y) && isFinite(p.z);
        }
        const handle=handleRepeater.itemAt(0), p=handle.mapToItem(null,12,12);
        return JSON.stringify({chunks:meshRepeater.count,vertices:vertices,finite:finite,gizmo:[p.x,p.y],handle:handle.visible});
    }

    function rayAt(x, y, select, extend) {
        const a = view.mapTo3DScene(Qt.vector3d(x, y, 1));
        const b = view.mapTo3DScene(Qt.vector3d(x, y, 2));
        const origin=[a.x,-a.z,a.y], direction=[b.x-a.x,a.z-b.z,b.y-a.y];
        if(authoring.visible) {
            if(authoring.pick(origin,direction,distance*.012,depthIndex,select,!!extend) || authoring.state.editing) return {};
        }
        return workspace.pick(origin, direction, depthIndex, select, distance*.012);
    }
    function screenPoint(axis) {
        if (!selected.id) return Qt.point(-100, -100);
        const p = selected.trs;
        const x = p[0] + (axis === 0 ? gizmoSize : 0);
        const y = p[1] + (axis === 1 ? gizmoSize : 0);
        const z = p[2] + (axis === 2 ? gizmoSize : 0);
        return projectPoint(x,y,z);
    }
    function projectPoint(x: real,y: real,z: real): point {
        const result=view.mapFrom3DScene(Qt.vector3d(x,z,-y));
        return Qt.point(result.x,result.y);
    }
    function pan(dx, dy) {
        const camera = orthographic ? orthoCamera : perspectiveCamera;
        const shift = camera.mapDirectionToScene(Qt.vector3d(-dx*distance/height, dy*distance/height, 0));
        cameraOrigin.position = cameraOrigin.position.plus(shift);
    }
    function storeCamera() {
        if (restoringCamera) return;
        const p=cameraOrigin.position, r=cameraOrigin.eulerRotation;
        workspace.saveCamera([p.x,-p.z,p.y,r.x,r.y,r.z,distance],orthographic);
    }
    function setView(name) {
        const rotations = {Front:[0,0,0], Right:[0,90,0], Top:[-90,0,0]};
        const angles = rotations[name];
        cameraOrigin.eulerRotation = Qt.vector3d(angles[0],angles[1],angles[2]);
        orthographic = true; viewName = name;
        cameraDirty = true; cameraSave.restart();
    }
    function refreshOverlays() {
        for (let i=0;i<handleRepeater.count;i++)
            handleRepeater.itemAt(i).endpoint = viewport.screenPoint(i);
        gizmoLines.requestPaint();
        anchorMarkers.requestPaint();
    }
    onOrthographicChanged: cameraSave.restart()

    View3D {
        id: view
        anchors.fill: parent
        camera: viewport.orthographic ? orthoCamera : perspectiveCamera
        environment: SceneEnvironment {
            backgroundMode: SceneEnvironment.Color
            clearColor: "#24262b"
            antialiasingMode: SceneEnvironment.MSAA
            antialiasingQuality: SceneEnvironment.High
        }
        Node {
            id: cameraOrigin
            eulerRotation: Qt.vector3d(-18, 25, 0)
            PerspectiveCamera {
                id: perspectiveCamera
                z: viewport.distance
                clipNear: Math.max(0.00001, viewport.distance/10000)
                clipFar: Math.max(1000, viewport.distance*100)
            }
            OrthographicCamera {
                id: orthoCamera
                z: viewport.distance
                clipNear: perspectiveCamera.clipNear
                clipFar: perspectiveCamera.clipFar
                horizontalMagnification: viewport.height/(viewport.distance*1.1)
                verticalMagnification: horizontalMagnification
            }
            // Camera-relative studio lights keep form readable throughout an orbit.
            DirectionalLight { eulerRotation: Qt.vector3d(-35,-35,0); brightness: 1.05; ambientColor: "#262930" }
            DirectionalLight { eulerRotation: Qt.vector3d(20,50,0); brightness: .3 }
            DirectionalLight { eulerRotation: Qt.vector3d(-20,160,0); brightness: .4 }
        }
        Model {
            visible: viewport.gridVisible
            eulerRotation.x: -90
            geometry: GridGeometry { horizontalLines: 41; verticalLines: 41; horizontalStep: .25; verticalStep: .25 }
            materials: DefaultMaterial { lighting: DefaultMaterial.NoLighting; diffuseColor: "#33363c"; cullMode: Material.NoCulling }
            opacity: .22
        }
        Node {
            eulerRotation.x: -90
            Model {
                visible: authoring.visible
                geometry: ControlGeometry { points: authoring.lines; segments: true }
                materials: DefaultMaterial { diffuseColor: "#5a9daa"; lighting: DefaultMaterial.NoLighting }
            }
            Model {
                visible: authoring.visible
                geometry: ControlGeometry { points: authoring.points; radius: viewport.distance*.0025 }
                materials: DefaultMaterial { diffuseColor: "#6fcbe1"; lighting: DefaultMaterial.NoLighting }
            }
            Model {
                visible: authoring.visible
                geometry: ControlGeometry { points: authoring.selectedPoints; radius: viewport.distance*.004 }
                materials: DefaultMaterial { diffuseColor: "#ffcc73"; lighting: DefaultMaterial.NoLighting }
            }
            Model {
                visible: authoring.visible
                geometry: ControlGeometry { points: authoring.hoveredPoints; radius: viewport.distance*.0045 }
                materials: DefaultMaterial { diffuseColor: "#ffffff"; lighting: DefaultMaterial.NoLighting }
            }
            Model {
                visible: authoring.visible
                geometry: ControlGeometry { points: authoring.hoveredLines; segments: true }
                materials: DefaultMaterial { diffuseColor: "#ffffff"; lighting: DefaultMaterial.NoLighting }
            }
            Repeater3D {
                id: meshRepeater
                model: workspace.meshModel
                delegate: Node {
                    required property var item
                    property alias meshNode: meshNode
                    position: Qt.vector3d(item.trs[0], item.trs[1], item.trs[2])
                    rotation: Qt.quaternion(item.quaternion[0], item.quaternion[1], item.quaternion[2], item.quaternion[3])
                    scale: Qt.vector3d(item.trs[6], item.trs[7], item.trs[8])
                    Model {
                        id: meshNode
                        visible: item.active
                        position: Qt.vector3d(item.geometry_offset[0], item.geometry_offset[1], item.geometry_offset[2])
                        geometry: MeshGeometry { assetId: item.handle; chunk: item.chunk }
                        opacity: item.readonly ? .08 : !viewport.xray ? 1 : item.id === workspace.selectedId ? .65 : item.id === workspace.hoveredId ? .5 : .3
                        materials: PrincipledMaterial {
                            baseColor: item.color
                            alphaMode: PrincipledMaterial.Opaque
                            roughness: .65
                            specularAmount: .25
                            cullMode: Material.NoCulling
                            emissiveFactor: item.id === workspace.selectedId ? Qt.vector3d(.015,.015,.015) :
                                            item.id === workspace.hoveredId ? Qt.vector3d(.035,.035,.035) : Qt.vector3d(0,0,0)
                        }
                    }
                    ResourceLoader { geometries: [meshNode.geometry] }
                }
            }
            Repeater3D {
                model: workspace.treeRows
                delegate: Model {
                    required property var modelData
                    visible: !modelData.asset && modelData.visible
                    position: Qt.vector3d(modelData.trs[0],modelData.trs[1],modelData.trs[2])
                    source: "#Sphere"
                    scale: Qt.vector3d(.0003,.0003,.0003)
                    opacity: modelData.opacity
                    materials: PrincipledMaterial { baseColor: "#d7bf78" }
                }
            }
        }
    }
    MouseArea {
        id: navigation
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.MiddleButton | Qt.RightButton
        property point previous: Qt.point(0,0)
        onPressed: function(mouse) {
            viewport.forceActiveFocus();
            previous = Qt.point(mouse.x,mouse.y);
            if (mouse.button !== Qt.LeftButton) return;
            viewport.depthIndex = mouse.modifiers & Qt.AltModifier ? viewport.depthIndex + 1 : 0;
            viewport.rayAt(mouse.x,mouse.y,!viewport.anchorMode,!!(mouse.modifiers & Qt.ShiftModifier));
            if (viewport.anchorMode) { workspace.lockAnchor(viewport.anchorMode); viewport.anchorMode = ""; }
        }
        onPositionChanged: function(mouse) {
            viewport.pointerPosition = Qt.point(mouse.x,mouse.y);
            if (!(pressedButtons & (Qt.MiddleButton | Qt.RightButton))) return;
            const dx = mouse.x-previous.x, dy = mouse.y-previous.y;
            if (mouse.modifiers & Qt.ShiftModifier) viewport.pan(dx,dy);
            else { cameraOrigin.eulerRotation = Qt.vector3d(cameraOrigin.eulerRotation.x-dy*.35,cameraOrigin.eulerRotation.y-dx*.35,0); viewport.viewName = "User view"; }
            previous = Qt.point(mouse.x,mouse.y);
            viewport.cameraDirty = true;
            cameraSave.restart();
        }
        onWheel: function(wheel) {
            viewport.distance = Math.max(.002, Math.min(100000, viewport.distance*Math.exp(-wheel.angleDelta.y/1000)));
            viewport.cameraDirty = true;
            cameraSave.restart();
        }
        onDoubleClicked: workspace.frameSelection()
    }
    Canvas {
        id: gizmoLines
        anchors.fill: parent
        visible: workspace.state.handles && !!viewport.selected.id && !viewport.selected.readonly
        function axis(context, center, index) {
            const end = viewport.screenPoint(index);
            context.strokeStyle = ["#f47779", "#7ed6a5", "#79b7ff"][index];
            context.beginPath(); context.moveTo(center.x,center.y); context.lineTo(end.x,end.y); context.stroke();
        }
        onPaint: {
            const context = getContext("2d");
            context.clearRect(0,0,width,height); context.lineWidth = 3;
            const center = viewport.screenPoint(-1);
            for (let i=0;i<3;i++) axis(context,center,i);
        }
    }
    Repeater {
        id: handleRepeater
        model: 3
        delegate: Rectangle {
            id: handle
            required property int index
            objectName: "gizmo_" + index
            property point endpoint: Qt.point(-100,-100)
            x: endpoint.x-12; y: endpoint.y-12
            width: 24; height: 24; radius: 12
            visible: workspace.state.handles && !!viewport.selected.id && !viewport.selected.readonly
            color: ["#c84d55", "#3b9a69", "#4283cb"][index]
            border.color: "#dae8ee"
            Label { anchors.centerIn: parent; text: ["X","Y","Z"][index]; color: "white"; font.bold: true }
            MouseArea {
                anchors.fill: parent
                property point startPoint
                property point projectedAxis
                property real worldSize
                onPressed: function(mouse) {
                    startPoint = mapToItem(viewport,mouse.x,mouse.y);
                    const center = viewport.screenPoint(-1), end = viewport.screenPoint(handle.index);
                    projectedAxis = Qt.point(end.x-center.x,end.y-center.y);
                    worldSize = viewport.gizmoSize;
                    workspace.beginTransform(viewport.toolMode);
                }
                onPositionChanged: function(mouse) {
                    if (!pressed) return;
                    const now = mapToItem(viewport,mouse.x,mouse.y);
                    const denominator = Math.max(100,projectedAxis.x*projectedAxis.x+projectedAxis.y*projectedAxis.y);
                    const amount = ((now.x-startPoint.x)*projectedAxis.x+(now.y-startPoint.y)*projectedAxis.y)/denominator*worldSize;
                    workspace.dragTransform(handle.index,amount);
                }
                onReleased: workspace.endTransform(false)
                onCanceled: workspace.endTransform(true)
            }
        }
    }
    Canvas {
        id: anchorMarkers; anchors.fill: parent
        visible: workspace.state.anchors && !!viewport.selected.id
        onPaint: {
            const ctx=getContext("2d"), points=viewport.selected.anchors || [];
            ctx.clearRect(0,0,width,height);
            for (let i=0;i<points.length;i+=3) {
                const p=view.mapFrom3DScene(Qt.vector3d(points[i],points[i+2],-points[i+1]));
                ctx.fillStyle=i === 0 ? "#ffcc64" : "#7bdcff";
                ctx.beginPath(); ctx.arc(p.x,p.y,i === 0 ? 6 : 3,0,2*Math.PI); ctx.fill();
            }
        }
    }
    Column {
        anchors.left: parent.left; anchors.bottom: parent.bottom; anchors.margins: 14; spacing: 5
        width: parent.width-28
        Label { text: viewport.viewName + (viewport.orthographic ? " · Orthographic" : " · Perspective"); color: Theme.muted; font.pixelSize: 11 }
        Label { visible: !!viewport.anchorMode; text: "Pick a " + (viewport.anchorMode === "FACE_CENTER" ? "face" : "vertex") + " on the selected child · Esc to cancel"; color: Theme.accent; wrapMode: Text.WordWrap; width: parent.width }
        Label { visible: workspace.state.publishing > 0; text: "Preparing viewport · " + workspace.state.publishing + " chunks pending"; color: Theme.accent }
        Label {
            visible: workspace.state.diagnostics
            text: Object.entries(workspace.metrics).map(function(pair) {
                return pair[0].replace(/_/g," ") + " " + pair[1].p95_ms.toFixed(1) + " ms";
            }).join(" · ")
            font.pixelSize: 10; color: "#9699a3"; width: parent.width; wrapMode: Text.WordWrap
        }
    }
    Row {
        anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 10; spacing: 4
        Repeater {
            model: ["Front","Right","Top"]
            UiButton { required property string modelData; text: modelData; flatStyle: true; hint: "Look from " + modelData.toLowerCase(); onClicked: viewport.setView(modelData) }
        }
        UiButton { glyph: "grid"; flatStyle: true; checked: viewport.gridVisible; checkable: true; hint: "Toggle reference grid (0.25 m spacing)"; onClicked: viewport.gridVisible = checked }
        UiButton { objectName: "xrayToggle"; text: "X-ray"; flatStyle: true; checked: viewport.xray; checkable: true; hint: "See through surfaces (Alt+Z)"; onClicked: viewport.xray = checked }
    }
    ColumnLayout {
        anchors.centerIn: parent; width: Math.min(320, parent.width-90); spacing: 14
        visible: workspace.treeRows.length === 0
        Image { source: "icons/mesh.svg"; sourceSize: Qt.size(40,40); opacity: .4; Layout.alignment: Qt.AlignHCenter }
        Label { text: "Start your assembly"; color: Theme.text; font.pixelSize: 22; Layout.alignment: Qt.AlignHCenter }
        Label { text: "Import your first primitive, then build its hierarchy and attachments."; color: Theme.muted; Layout.fillWidth: true; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; lineHeight: 1.4 }
        UiButton { text: "Import mesh…"; glyph: "import"; primary: true; Layout.alignment: Qt.AlignHCenter; onClicked: viewport.importRequested() }
        Label { text: "OBJ · STL · PLY  /  Ctrl+I"; color: Theme.muted; font.pixelSize: 11; Layout.alignment: Qt.AlignHCenter }
    }
    Timer {
        id: cameraSave; interval: 250; onTriggered: viewport.storeCamera()
    }
    Timer {
        interval: 33; repeat: true; running: true
        onTriggered: {
            if (viewport.pointerPosition.x !== viewport.previousPointer.x ||
                viewport.pointerPosition.y !== viewport.previousPointer.y || viewport.cameraDirty) {
                if (viewport.pointerPosition.x >= 0) viewport.rayAt(viewport.pointerPosition.x,viewport.pointerPosition.y,false);
                viewport.previousPointer = viewport.pointerPosition;
                viewport.cameraDirty = false;
            }
            viewport.refreshOverlays();
        }
    }
    Connections {
        target: workspace
        function onFrameRequested(values) {
            cameraOrigin.position = Qt.vector3d(values[0],values[2],-values[1]);
            viewport.distance = values[3]; viewport.cameraDirty = true;
            cameraSave.restart();
        }
        function onCameraRequested(values, orthographic) {
            viewport.restoringCamera = true;
            cameraOrigin.position = Qt.vector3d(values[0],values[2],-values[1]);
            cameraOrigin.eulerRotation = Qt.vector3d(values[3],values[4],values[5]);
            viewport.distance = values[6]; viewport.orthographic = orthographic;
            viewport.restoringCamera = false; cameraSave.stop(); viewport.cameraDirty = true;
        }
        function onChanged() { viewport.refreshOverlays(); }
    }
}

