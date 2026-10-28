"""Independent source-local region IDs never alias after topology guide assembly."""

import numpy as np
import pytest

from anthroforge.native import skin_guide_batch
from anthroforge.native.mesh import NativeCancellation
from anthroforge.native.skin_guides import Guides


def source(owner=7):
    samples = np.array([[0, 0, 0, 1, 0, 0, 0, 0, 1, owner]], dtype=float)
    return Guides(samples, np.array([[0, 0, 0], [1, 0, 0]], dtype=float), np.array([0, 2]))


def test_merge_isolates_sources_and_remaps_paths(session):
    first, second = source(), source()
    result = skin_guide_batch.merge(session.engine, (first, second))
    np.testing.assert_array_equal(result.samples[:, 9], [0, 1])
    np.testing.assert_array_equal(result.regions, [[0, 7], [1, 7]])
    np.testing.assert_array_equal(result.offsets, [0, 2, 4])
    np.testing.assert_array_equal(first.samples[:, 9], [7])
    np.testing.assert_array_equal(result.points, np.vstack((first.points, second.points)))


def test_empty_batch_has_valid_empty_contract(session):
    result = skin_guide_batch.merge(session.engine, ())
    assert result.samples.shape == (0, 10) and result.points.shape == (0, 3)
    assert result.regions.shape == (0, 2)
    np.testing.assert_array_equal(result.offsets, [0])


def test_invalid_offsets_and_nonfinite_samples_rejected(session):
    item = source()
    with pytest.raises(ValueError, match="path"):
        skin_guide_batch.merge(session.engine, (Guides(item.samples, item.points, [0, 1, 2]),))
    item.samples[0, 3] = np.nan
    with pytest.raises(ValueError, match="Nonfinite"):
        skin_guide_batch.merge(session.engine, (item,))


def test_cancelled_batch_does_not_publish_partial_sources(session):
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_guide_batch.merge(session.engine, (source(),), cancel.handle)
