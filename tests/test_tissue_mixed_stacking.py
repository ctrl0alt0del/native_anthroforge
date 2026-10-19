"""Surface construction capability, rather than anatomical label, selects stacking adapters."""

import numpy as np
import pytest

from tests.test_tissue_stack_workflow import assembly, current


def normal(session, target, relaxed=False):
    session.command(
        "tissue.inflation", target=target, changes=dict(mode="NORMAL", amount=0.025, minimum=0.002)
    )
    if relaxed:
        session.command(
            "tissue.relaxation",
            target=target,
            changes=dict(mode="GEOMETRIC", sagginess=0.05, sag_limit=0.002),
        )


@pytest.mark.parametrize(
    "provider,receiver,relaxed",
    [(True, False, False), (False, True, False), (True, True, False), (False, True, True)],
)
def test_surface_shells_stack_in_both_roles_with_exact_backing(
    session, provider, receiver, relaxed
):
    _, a, b = assembly(session)
    if provider:
        normal(session, a)
    if receiver:
        normal(session, b, relaxed)
    session.wait(30)
    current(session, a)
    points = current(session, b)
    item = session.document.object(b)
    assert item.stack_plan.providers == (a,)
    if receiver:
        assert_backing(session, item, points)


def assert_backing(session, item, points):
    count = session.assets[item.base_result.asset].mesh.counts[0]
    own = session.assets[item.intrinsic_result.asset].mesh.array(0)
    np.testing.assert_array_equal(points[count:], own[count:])
