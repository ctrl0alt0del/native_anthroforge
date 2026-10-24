"""Conflicting inherited planes retain the accepted spatial instance across saving."""

from dataclasses import replace

from anthroforge.application.storage import decode_document, document_state
from anthroforge.core.construction import CurvePoint
from anthroforge.core.fibers import Fiber, FiberBinding
from anthroforge.core.mirroring import MirrorRule
from tests.test_mirroring import hierarchy


def attached_document():
    points = tuple(CurvePoint(position=p) for p in ((0, 0, 0), (1, 1, 1)))
    bindings = tuple(
        FiberBinding(p.id, target) for p, target in zip(points, ("child", "tip"), strict=True)
    )
    item = Fiber(name="Shared fiber", points=points, bindings=bindings)
    document = replace(hierarchy(), objects=(item,))
    return document, item


def test_incompatible_plane_retains_previous_instance_and_accepted_frame_on_reload():
    document, item = attached_document()
    identity = f"mirror/root/{item.id}"
    accepted = document.mirrors.plane(document.mirrors.instances[identity])
    rules = (*document.mirror_rules, MirrorRule("tip", enabled=True, axis="Y"))
    conflicting = replace(document, mirror_rules=rules)
    assert item.id in conflicting.mirrors.conflicts
    assert conflicting.mirrors.plane(conflicting.mirrors.instances[identity]) == accepted
    restored = decode_document(document_state(conflicting))
    assert restored.mirrors.plane(restored.mirrors.instances[identity]).frame == accepted.frame


def test_association_alone_does_not_mirror_unused_construction():
    from anthroforge.core.points import Point

    document = replace(hierarchy(), objects=(Point(name="Unused", owners=("child",)),))
    assert not any(v.source == document.objects[0].id for v in document.mirrors.instances.values())
