"""Project candidate services own their context teardown."""

from typing import Any

from .assembly_runtime import Assembly
from .reconstruction_comparison import Comparison
from .service_lifecycle import Event, Service
from .skeleton_runtime import SkeletonUpdate
from .variant_review import VariantReview


def attach(session: Any) -> Service:
    session.assembly = Assembly(session)
    session.skeleton_update = SkeletonUpdate(session)
    session.variant_review = VariantReview(session)
    session.reconstruction_comparison = Comparison(session)
    return Service(
        "preparation",
        (
            (Event.CLOSE, session.assembly.cancel),
            (Event.CLOSE, session.skeleton_update.cancel),
            (Event.CLOSE, session.variant_review.cancel),
            (Event.CLOSE, session.reconstruction_comparison.cancel),
        ),
    )
