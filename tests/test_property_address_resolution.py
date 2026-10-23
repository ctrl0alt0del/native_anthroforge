"""Direct property reads retain discovery metadata and reject noncanonical addresses."""

from dataclasses import replace

import pytest

from anthroforge.application import property_catalog
from anthroforge.core.numeric_properties import PropertyRef
from tests.test_tissue_field_editing import create as create_field
from tests.test_tissue_workflow import assembly


def target(session, kind):
    if kind == "TISSUE":
        key = assembly(session)[-1]
        create_field(session, key, "left/right:α")
        return key
    if kind == "LATTICE":
        return session.command("control.create", kind=kind)
    if kind == "SEGMENT_CHAIN":
        return session.command("primitive.create", kind=kind)
    settings = dict(resolution=8) if kind == "PARAMETRIC" else {}
    return session.command("curve.create", engine=kind, settings=settings)


@pytest.mark.parametrize("kind", ["BEZIER", "PARAMETRIC", "LATTICE", "SEGMENT_CHAIN", "TISSUE"])
def test_direct_resolution_preserves_every_discovered_descriptor(session, kind):
    key = target(session, kind)
    session.wait(5)
    document = session.document
    descriptors = list(property_catalog.descriptors(document.object(key)))
    assert descriptors
    for expected in descriptors:
        assert property_catalog.resolve(document, expected.reference) == expected
        component = replace(expected.reference, component=expected.components - 1)
        assert property_catalog.resolve(document, component) == replace(
            expected, reference=component
        )


@pytest.mark.parametrize(
    "path",
    [
        ("matrix",),
        ("result", "revision"),
        ("closed",),
        ("points", "#0", "radius"),
        ("transform", "position", "#0"),
    ],
)
def test_direct_resolution_rejects_ineligible_state_and_positional_point_aliases(session, path):
    key = target(session, "BEZIER")
    with pytest.raises(ValueError):
        property_catalog.resolve(session.document, PropertyRef(key, path))


def test_positional_arrays_require_canonical_indices_and_valid_components(session):
    key = target(session, "LATTICE")
    for token in ("#01", "#-1", "#99"):
        with pytest.raises(ValueError):
            property_catalog.resolve(session.document, PropertyRef(key, ("points", token), 0))
    with pytest.raises(ValueError, match="component"):
        property_catalog.resolve(session.document, PropertyRef(key, ("points", "#1"), 3))


def test_parametric_coordinates_and_expression_intervals_remain_readonly(session):
    key = target(session, "PARAMETRIC")
    session.command(
        "curve.parametric.configure", curve=key, changes=dict(interval=dict(end_expression="2*pi"))
    )
    session.wait(5)
    point = session.document.object(key).points[0].id
    for path in (("points", "@" + point, "position"), ("engine_settings", "interval", "end")):
        value = property_catalog.resolve(session.document, PropertyRef(key, path))
        assert not value.writable and "controlled" in value.reason
