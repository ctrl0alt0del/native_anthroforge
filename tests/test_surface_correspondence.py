"""Retained material stations, rather than moving arclength, define authored lofts."""

import numpy as np
import pytest

from anthroforge.application.curve_independence import remapped_surface
from anthroforge.application.object_codec import decode, encode
from anthroforge.core.surfaces import SurfaceAlignment
from anthroforge.native import curve_surfaces as native
from tests.test_native_surfaces import row
from tests.test_surface_workflow import surface, vertices


def inputs(engine):
    first = row(engine, [[0, 0, 0], [0.1, 0, 1], [1, 0, 0]])
    second = row(engine, [[0, 1, 0], [0.8, 1, 1], [1, 1, 0]])
    return [native.correspondence(r, [(0, 0), (1, 0.4), (2, 2)]) for r in (first, second)]


def test_native_station_mapping_preserves_sections_and_normalizes_domain(session):
    rows = inputs(session.engine)
    mesh = native.geometry(session.engine, rows, [1], native.Settings())
    expected = [[0, 0.5, 0], [0.45, 0.5, 1], [1, 0.5, 0]]
    np.testing.assert_allclose(mesh.array(0)[3:6], expected)
    assert len(mesh.array(0)) == 9
    for value in rows:
        value.reverse = True
    mirrored = native.geometry(session.engine, rows, [1], native.Settings())
    np.testing.assert_allclose(mirrored.array(0)[3:6], expected[::-1])


@pytest.mark.parametrize("settings", [native.Settings(exact=False), native.Settings()])
def test_native_mapping_rejects_incompatible_sampling(session, settings):
    rows = inputs(session.engine)
    if settings.exact:
        rows[0].span = 0.5
    with pytest.raises(ValueError, match="complete open"):
        native.geometry(session.engine, rows, [1], settings)


def setup(session):
    curves = []
    for y, middle in ((0, 0.1), (1, 0.8)):
        points = [dict(position=p) for p in ((0, y, 0), (middle, y, 1), (1, y, 0))]
        curves.append(session.command("curve.create", points=points, engine="POLYLINE"))
    session.wait()
    target = surface(session, curves)
    session.command(
        "surface.correspondence", target=target, mapping=mapping(session, curves), across=[1]
    )
    session.wait()
    return target, curves


def mapping(session, curves):
    return {
        key: [
            (p.id, v) for p, v in zip(session.document.object(key).points, (0, 0.4, 2), strict=True)
        ]
        for key in curves
    }


def test_authored_mapping_roundtrip_copy_and_undo(session, tmp_path):
    target, curves = setup(session)
    original = session.document.object(target)
    assert decode(encode(original)) == original
    mapping = {p.id: "new_" + p.id for key in curves for p in session.document.object(key).points}
    copied = remapped_surface(original, mapping)
    assert copied.alignment[0].stations[0][0].startswith("new_")
    verify_roundtrip(session, target, tmp_path)
    session.command("surface.realign", target=target)
    session.wait()
    assert not any(a.stations for a in session.document.object(target).alignment)
    session.command("undo")
    session.wait()
    assert session.document.object(target).alignment == original.alignment


def verify_roundtrip(session, target, tmp_path):
    before = vertices(session, target)
    path = str(tmp_path / "mapped.anthroforge")
    session.command("save", path=path, blocked_policy="wait")
    session.command("open", path=path)
    session.command("evaluate", entities=[target])
    session.wait()
    np.testing.assert_array_equal(vertices(session, target), before)


def test_deformation_keeps_material_sections_and_stale_mapping_fails(session):
    target, curves = setup(session)
    point = session.document.object(curves[0]).points[1].id
    session.command("curve.point.update", curve=curves[0], point=point, position=[0.3, 0, 1])
    session.wait()
    np.testing.assert_allclose(vertices(session, target)[4], [0.55, 0.5, 1])
    from anthroforge.application.surface_evaluation import correspondence

    with pytest.raises(ValueError, match="removed"):
        correspondence(native.Row(), SurfaceAlignment(stations=(("a", 0), ("b", 1))), {})


def test_invalid_material_station_identity_and_order():
    with pytest.raises(ValueError, match="strictly increasing"):
        SurfaceAlignment(stations=(("a", 0), ("b", 0)))
    with pytest.raises(ValueError, match="distinct"):
        SurfaceAlignment(stations=(("a", 0), ("a", 1)))
