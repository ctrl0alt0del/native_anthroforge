"""Complete-shell checks cover backing/rims that are absent from the participating side."""

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.core.tissue_settings import TissueInflation
from anthroforge.native import tissue_shapes
from anthroforge.native.mesh import NativeCancellation
from anthroforge.native.stacking import StackSession, surface
from anthroforge.native.tissue_stacking import MaterialLease, assemble
from tests.stacking_material_fixtures import arrays, ordinary
from tests.test_tissue_inflation import grid_mesh
from tests.test_tissue_stack_material import INFLATIONS


def shell(session):
    base = grid_mesh(session.engine, INFLATIONS[0]["points"])
    config = ordinary(TissueInflation(mode="NORMAL", amount=0.04, minimum=0.01))
    own = tissue_shapes.normal(base, config.parts[0].a.inflation)
    lease = MaterialLease(base, own, own, config)
    return own, lease


def test_full_shell_validates_outer_motion_with_exact_unchanged_backing(session):
    own, lease = shell(session)
    result = assemble(lease, arrays(lease.domain(1))["own"] + [0, 0, 0.005])
    StackSession(session.engine).validate_surfaces([surface(own, result, IDENTITY)])
    count = lease.domain(1).vertices
    np.testing.assert_array_equal(result.array(0)[count:], own.array(0)[count:])


def test_complete_validation_rejects_rim_inversion_omitted_by_outer_side(session):
    own, lease = shell(session)
    domain = arrays(lease.domain(1))
    result = assemble(lease, 2 * domain["base"] - domain["own"])
    with pytest.raises(ValueError, match="FOLD|COLLAPSE|INTERSECTION"):
        StackSession(session.engine).validate_surfaces([surface(own, result, IDENTITY)])


def test_complete_validation_is_cancellable(session):
    own, _ = shell(session)
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel|CANCELLED"):
        StackSession(session.engine).validate_surfaces([surface(own, own, IDENTITY)], token.handle)
