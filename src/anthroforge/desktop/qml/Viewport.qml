import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick3D
import QtQuick3D.Helpers
import AnthroForge.Native 1.0

Item {
    id: viewport
    clip: true
    signal importRequested()
    property var keyboard: inactiveInput
    QtObject {
        id: inactiveInput
        readonly property bool blocked: true
        readonly property int modifiers: 0
        function held(action) { return false; }
        function matches(action, mask) { return false; }
        function shortcut(command) { return ""; }
    }
    property bool gridVisible: true
    property bool xray: false
    property string viewName: "User view"
    property string toolMode: "Move"
    property string anchorMode: ""
    property bool orthographic: false
    readonly property vector3d imageViewAxis: Qt.vector3d(view.camera.forward.x, -view.camera.forward.z, view.camera.forward.y)
    readonly property string imageAlignmentAxis: !orthographic ? "" : Math.abs(imageViewAxis.x)>0.999999 ? "X" : Math.abs(imageViewAxis.y)>0.999999 ? "Y" : Math.abs(imageViewAxis.z)>0.999999 ? "Z" : ""
    onImageViewAxisChanged: workspace.setViewportDirection([imageViewAxis.x,imageViewAxis.y,imageViewAxis.z])
    property real distance: 4
    property int depthIndex: 0
    property point pointerPosition: Qt.point(-1, -1)
    property point previousPointer: Qt.point(-2, -2)
    property bool cameraDirty: true
    property bool restoringCamera: false
    property var preservedCamera: null
    readonly property bool canRestoreView: preservedCamera !== null
    readonly property bool drawing: workspace.drawingTools.state.active
    readonly property bool measuring: drawing || workspace.inspectionTools.state.active || workspace.imageTools.state.active
    readonly property var selected: authoring.transformData
    readonly property bool transformAvailable: !!selected.id && !!selected.transformable && !selected.readonly && !workspace.state.waiting
    readonly property bool modalTransforming: modalTransform.active
    readonly property bool transforming: gizmo.dragging || curveEditor.dragging || modalTransforming || workspace.drawingTools.state.painting
    readonly property bool snapping: keyboard.held("snapSurface") && authoring.active &&
        (curveEditor.dragging || (gizmo.dragging && toolMode==="Move") || (modalTransforming && modalTransform.gesture.mode==="Move"))
    readonly property bool insertionPreview: curveEditor.previewActive
    readonly property bool navigating: !!(navigation.pressedButtons & (Qt.MiddleButton | Qt.RightButton))
    readonly property var cameraState: [cameraOrigin.x,cameraOrigin.y,cameraOrigin.z,cameraOrigin.eulerRotation.x,cameraOrigin.eulerRotation.y,cameraOrigin.eulerRotation.z,orthographic]
    readonly property real gizmoSize: distance * 1.1 * 90 / Math.max(1,height)

    function inspectScene(): string {
        let vertices = 0, finite = true;
        for (let i=0;i<meshRepeater.count;i++) {
            const node=meshRepeater.objectAt(i), model=node.meshNode, p=model.scenePosition;
            vertices += model.geometry.vertexCount;
            finite = finite && isFinite(p.x) && isFinite(p.y) && isFinite(p.z);
        }
        const p=gizmo.probe(0);
        const c=cameraOrigin.position, r=cameraOrigin.eulerRotation;
        return JSON.stringify({chunks:meshRepeater.count,vertices:vertices,finite:finite,gizmo:[p.x,p.y],handle:gizmo.visible,
            camera:[c.x,-c.z,c.y,r.x,r.y,r.z,distance],orthographic:orthographic,selected:workspace.selectedId});
    }

    function cameraPoint(x,y,depth) {
        if(orthographic) return Qt.vector3d((x-width/2)/orthoCamera.horizontalMagnification,(height/2-y)/orthoCamera.verticalMagnification,-depth);
        const extent=perspectiveCamera.fieldOfViewOrientation===PerspectiveCamera.Horizontal?width:height;
        const factor=2*depth*Math.tan(perspectiveCamera.fieldOfView*Math.PI/360)/Math.max(1,extent);
        return Qt.vector3d((x-width/2)*factor,(height/2-y)*factor,-depth);
    }
    function worldRay(x,y) {
        const camera=view.camera;
        const a=camera.mapPositionToScene(cameraPoint(x,y,camera.clipNear));
        const local=orthographic?Qt.vector3d(0,0,-1):cameraPoint(x,y,1);
        const d=camera.mapDirectionToScene(local);
        return {origin:[a.x,-a.z,a.y],direction:[d.x,-d.z,d.y]};
    }
    function rayAt(x, y, select, extend) {
        if(drawing) return {};
        const ray=worldRay(x,y), origin=ray.origin, direction=ray.direction;
        if(workspace.imageTools.state.active) { workspace.imageTools.probe(origin,direction,select); return {}; }
        if(measuring) { workspace.inspectionTools.probe(origin,direction,depthIndex,select); return {}; }
        if(authoring.visible) {
            if(authoring.pick(origin,direction,distance*.012,depthIndex,select,!!extend) || authoring.state.editing) return {};
        }
        return workspace.pick(origin, direction, depthIndex, select, distance*.012, !!extend);
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
        const p=view.camera.mapPositionFromScene(Qt.vector3d(x,z,-y));
        const magnification=pixelsPerUnit(-p.z);
        return Qt.point(width/2+p.x*magnification,height/2-p.y*magnification);
    }
    function pointInFront(point) {
        return view.camera.mapPositionFromScene(Qt.vector3d(point[0],point[2],-point[1])).z < -view.camera.clipNear;
    }
    function formatLength(value) { return (value/workspace.state.unit_factor).toFixed(3)+" "+workspace.state.display_units; }
    function pixelsPerUnit(depth) {
        if(orthographic) return orthoCamera.verticalMagnification;
        const extent=perspectiveCamera.fieldOfViewOrientation===PerspectiveCamera.Horizontal?width:height;
        return extent/(2*Math.max(perspectiveCamera.clipNear,depth)*Math.tan(perspectiveCamera.fieldOfView*Math.PI/360));
    }
    function cancelTransform() { modalTransform.finish(true); curveEditor.finish(true); gizmo.cancel(); workspace.endTransform(true); }
    function confirmTransform() { if(drawing) workspace.drawingTools.finish(); else if(modalTransforming) modalTransform.finish(false); }
    function startModalTransform(mode) { if(!measuring) modalTransform.begin(mode); }
    function applyBookmark(values, orthographic, name) {
        if(!canRestoreView) preservedCamera=captureCamera();
        workspace.rebaseTransform();
        cameraOrigin.position=Qt.vector3d(values[0],values[2],-values[1]);
        cameraOrigin.eulerRotation=Qt.vector3d(values[3],values[4],values[5]);
        distance=values[6]; viewport.orthographic=orthographic; viewName=name;
        finishCameraChange();
    }
    function updateTransform() { curveEditor.updateDrag(); gizmo.updateDrag(pointerPosition); modalTransform.update(); }
    function surfaceOffset(steps) {
        const p=selected.trs, local=view.camera.mapPositionFromScene(Qt.vector3d(p[0],p[2],-p[1]));
        const step=8/pixelsPerUnit(-local.z)*(keyboard.held("precision") ? .1 : 1);
        authoring.curveInteraction.adjustOffset(steps*step); updateTransform();
    }
    function resetSurfaceOffset() { authoring.curveInteraction.resetOffset(); updateTransform(); }
    function screenTranslation(delta) {
        return screenTranslationAt(delta,selected.trs);
    }
    function screenTranslationAt(delta,pivot) {
        const camera=view.camera, local=camera.mapPositionFromScene(Qt.vector3d(pivot[0],pivot[2],-pivot[1]));
        const depth=Math.max(camera.clipNear,-local.z);
        const offset=cameraPoint(width/2+delta.x,height/2+delta.y,depth).minus(cameraPoint(width/2,height/2,depth));
        const d=camera.mapDirectionToScene(offset);
        return [d.x,-d.z,d.y];
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
        const angles = rotations[name], center=workspace.selectionCenter();
        if(!angles) return;
        if(!canRestoreView) preservedCamera=captureCamera();
        workspace.rebaseTransform();
        centerView(center);
        cameraOrigin.eulerRotation = Qt.vector3d(angles[0],angles[1],angles[2]);
        orthographic = true; viewName = name;
        finishCameraChange();
    }
    function captureCamera() {
        const p=cameraOrigin.position, r=cameraOrigin.eulerRotation;
        return {position:[p.x,p.y,p.z],rotation:[r.x,r.y,r.z],
            distance:distance,orthographic:orthographic,name:viewName};
    }
    function restoreView() {
        if(!canRestoreView) return;
        const saved=preservedCamera, p=saved.position, r=saved.rotation;
        workspace.rebaseTransform();
        cameraOrigin.position=Qt.vector3d(p[0],p[1],p[2]);
        cameraOrigin.eulerRotation=Qt.vector3d(r[0],r[1],r[2]);
        distance=saved.distance;
        orthographic=saved.orthographic;
        viewName=saved.name;
        preservedCamera=null;
        finishCameraChange();
    }
    function finishCameraChange() {
        curveEditor.rebase();
        gizmo.rebase();
        modalTransform.rebase();
        cameraDirty=true;
        cameraSave.restart();
    }
    function centerView(center) {
        if(!center.length) return;
        const position=Qt.vector3d(center[0],center[2],-center[1]);
        const depth=-view.camera.mapPositionFromScene(position).z;
        if(!orthographic) distance=height/(pixelsPerUnit(depth)*1.1);
        cameraOrigin.position=position;
    }
    function refreshOverlays() {
        anchorMarkers.requestPaint();
        measurementOverlay.requestPaint();
    }
    onOrthographicChanged: { workspace.setViewportProjection(orthographic); cameraSave.restart(); }

    Rectangle { anchors.fill: parent; color: "#24262b" }
    ImageLayer {
        id: backImages; anchors.fill: parent; sourceCamera: view.camera; orthographic: viewport.orthographic; viewAxis: viewport.imageViewAxis
        depthLayer: "BACK"
    }
    View3D {
        id: view
        anchors.fill: parent
        camera: viewport.orthographic ? orthoCamera : perspectiveCamera
        environment: SceneEnvironment {
            backgroundMode: SceneEnvironment.Transparent
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
        PathScene {}
        Node {
            id: worldScene
            eulerRotation.x: -90
            ImageScene { layer: "NORMAL"; orthographic: viewport.orthographic; viewAxis: viewport.imageViewAxis }
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
                        objectName: "surface_" + item.id + "_" + item.chunk
                        visible: item.active
                        position: Qt.vector3d(item.geometry_offset[0], item.geometry_offset[1], item.geometry_offset[2])
                        geometry: MeshGeometry { assetId: item.handle; chunk: item.chunk }
                        opacity: item.readonly ? .08 : authoring.state.editing && item.id === workspace.selectedId && ["LOFT","BODY"].indexOf(authoring.state.primitive?.kind) >= 0 ? .35 : !viewport.xray ? 1 : item.id === workspace.selectedId ? .65 : item.id === workspace.hoveredId ? .5 : .3
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
                    Node {
                        parent: selectionOutline.sceneRoot
                        position: Qt.vector3d(item.trs[0],item.trs[1],item.trs[2])
                        rotation: Qt.quaternion(item.quaternion[0],item.quaternion[1],item.quaternion[2],item.quaternion[3])
                        scale: Qt.vector3d(item.trs[6],item.trs[7],item.trs[8])
                        Model {
                            objectName: "mask_" + item.key
                            visible: item.active && (item.id === workspace.selectedId || (!viewport.xray && !item.readonly))
                            position: meshNode.position
                            geometry: meshNode.geometry
                            materials: DefaultMaterial { lighting: DefaultMaterial.NoLighting; diffuseColor: item.id === workspace.selectedId ? "white" : "black"; cullMode: Material.NoCulling }
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
    ImageLayer {
        id: frontImages; anchors.fill: parent; sourceCamera: view.camera; orthographic: viewport.orthographic; viewAxis: viewport.imageViewAxis
        depthLayer: "FRONT"
    }
    SelectionOutline {
        id: selectionOutline; objectName: "selectionOutline"; anchors.fill: parent
        sourceCamera: view.camera; orthographic: viewport.orthographic
        visible: !!workspace.selectedData.asset && !!workspace.selectedData.surface_visible
    }
    AuthoringView {
        anchors.fill: parent; sourceCamera: view.camera
        orthographic: viewport.orthographic; distance: viewport.distance
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
            viewport.depthIndex = keyboard.matches("deeperSelection",mouse.modifiers) ? viewport.depthIndex + 1 : 0;
            viewport.rayAt(mouse.x,mouse.y,!viewport.anchorMode,keyboard.matches("extendSelection",mouse.modifiers));
            if (viewport.anchorMode) { workspace.lockAnchor(viewport.anchorMode); viewport.anchorMode = ""; }
        }
        onPositionChanged: function(mouse) {
            viewport.pointerPosition = Qt.point(mouse.x,mouse.y);
            if (!(pressedButtons & (Qt.MiddleButton | Qt.RightButton))) return;
            const dx = mouse.x-previous.x, dy = mouse.y-previous.y;
            if (keyboard.matches("pan",mouse.modifiers)) viewport.pan(dx,dy);
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
        onDoubleClicked: { if(!viewport.measuring) workspace.frameSelection(); }
    }
    TransformGizmo { id: gizmo; objectName: "transformGizmo"; anchors.fill: parent; viewport: viewport; enabled: !viewport.measuring }
    CurveEditor { id: curveEditor; objectName: "curveEditor"; anchors.fill: parent; viewport: viewport; keyboard: viewport.keyboard; enabled: !viewport.measuring }
    CurveFeedback { anchors.fill: parent; viewport: viewport }
    ModalTransform { id: modalTransform; objectName: "modalTransform"; anchors.fill: parent; viewport: viewport }
    MeasurementOverlay { id: measurementOverlay; viewport: viewport }
    ImageCalibrationOverlay { viewport: viewport }
    DrawingOverlay { viewport: viewport }
    InspectionTools { viewport: viewport; anchors.right: parent.right; anchors.bottom: parent.bottom; anchors.margins: 12; z: 10 }
    Connections {
        target: workspace.inspectionTools
        function onBookmarkRequested(values, orthographic, name) { viewport.applyBookmark(values,orthographic,name); }
    }
    Canvas {
        id: anchorMarkers; anchors.fill: parent
        visible: workspace.state.anchors && !workspace.state.hidden_categories.includes("anchors") && !!viewport.selected.id
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
        Label { visible: viewport.snapping; text: "Wheel: surface offset · Middle click: reset · Release snapping modifier: reset"; color: Theme.snapColor; font.pixelSize: 11 }
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
            model: [{name:"Right",axis:"X",command:"viewX"},{name:"Front",axis:"Y",command:"viewY"},{name:"Top",axis:"Z",command:"viewZ"}]
            UiButton { required property var modelData; objectName: modelData.command; text: modelData.axis+" · "+keyboard.shortcut(modelData.command); flatStyle: true; hint: modelData.name+" view · Center selection and preserve zoom"; onClicked: viewport.setView(modelData.name) }
        }
        UiButton { objectName: "restoreView"; text: "Restore · "+keyboard.shortcut("restoreView"); flatStyle: true; enabled: viewport.canRestoreView; hint: "Restore the view before axis alignment, including zoom and projection"; onClicked: viewport.restoreView() }
        UiButton { glyph: "grid"; flatStyle: true; checked: viewport.gridVisible; checkable: true; hint: "Toggle reference grid (0.25 m spacing)"; onClicked: viewport.gridVisible = checked }
        UiButton { objectName: "xrayToggle"; text: "X-ray"; flatStyle: true; checked: viewport.xray; checkable: true; hint: "See through surfaces (Alt+Z)"; onClicked: viewport.xray = checked }
    }
    ColumnLayout {
        anchors.centerIn: parent; width: Math.min(320, parent.width-90); spacing: 14
        visible: workspace.state.object_count === 0 && !viewport.drawing
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
                if (viewport.pointerPosition.x >= 0 && !viewport.insertionPreview && !viewport.transforming) viewport.rayAt(viewport.pointerPosition.x,viewport.pointerPosition.y,false);
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
            viewport.preservedCamera = null;
            viewport.viewName = "User view";
            cameraOrigin.position = Qt.vector3d(values[0],values[2],-values[1]);
            cameraOrigin.eulerRotation = Qt.vector3d(values[3],values[4],values[5]);
            viewport.distance = values[6]; viewport.orthographic = orthographic;
            viewport.restoringCamera = false; cameraSave.stop(); viewport.cameraDirty = true;
        }
        function onChanged() { viewport.refreshOverlays(); }
    }
}

