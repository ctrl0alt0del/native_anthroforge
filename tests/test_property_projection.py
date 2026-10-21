from dataclasses import replace

import numpy as np
import pytest
from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine

from anthroforge.application.primitive_operations import default_primitive
from anthroforge.desktop.property_projection import PropertyProjection

OBSERVER = b"""import QtQml
QtObject {
    property var curves: projection.curves
    property int replacements: 0
    property real x: curves[0].points[0].position[0]
    onCurvesChanged: replacements += 1
}"""


def observer(projection):
    engine = QQmlEngine()
    engine.rootContext().setContextProperty("projection", projection)
    component = QQmlComponent(engine)
    component.setData(OBSERVER, QUrl())
    value = component.create()
    assert value, component.errors()
    return engine, component, value


@pytest.mark.parametrize("number", [float, np.float64, np.float32])
def test_point_edit_updates_value_without_replacing_curve_choices(number):
    app = QCoreApplication.instance() or QCoreApplication([])
    curve = default_primitive("BODY", "CAPSULE").curves[0]
    projection = PropertyProjection()
    projection.synchronize(dict(curves=(curve,)))
    engine, component, value = observer(projection)
    before = value.property("replacements")
    point = replace(curve.points[0], position=(number(2.0), number(0.0), number(0.0)))
    projection.synchronize(dict(curves=(replace(curve, points=(point, *curve.points[1:])),)))
    assert value.property("x") == 2.0
    assert value.property("replacements") == before
    assert app and engine and component
    value.deleteLater()


def test_reordering_and_removing_records_preserves_retained_identity():
    app = QCoreApplication.instance() or QCoreApplication([])
    projection = PropertyProjection()
    projection.synchronize(dict(rows=[dict(id="a", name="A"), dict(id="b", name="B")]))
    a, b = projection.value("rows")
    projection.synchronize(dict(rows=[dict(id="b", name="Renamed"), dict(id="a", name="A")]))
    assert projection.value("rows") == [b, a] and b.value("name") == "Renamed"
    projection.synchronize(dict(rows=[dict(id="b", name="Renamed")]))
    assert projection.value("rows") == [b]
    assert projection.updateValue("rows", []) == [b]
    assert app


def test_command_projection_is_owned_snapshot_with_nested_values():
    from anthroforge.desktop.controller_actions import command_values

    app = QCoreApplication.instance() or QCoreApplication([])
    projection = PropertyProjection()
    projection.synchronize(dict(profile=dict(depths=[0.01, 0.02], segments=4.0)))
    result = command_values(dict(value=projection.value("profile")))
    projection.synchronize(dict(profile=dict(depths=[0.03, 0.04], segments=6.0)))
    assert result == dict(value=dict(depths=[0.01, 0.02], segments=4))
    assert type(result["value"]["segments"]) is int and app
