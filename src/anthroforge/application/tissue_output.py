"""Owned phase output bundles separate captured source state from generated geometry."""

from dataclasses import dataclass

from anthroforge.core.tissue_base import TissueBaseState
from anthroforge.native.mesh import Mesh


@dataclass(frozen=True)
class TissueOutput:
    mesh: Mesh | None = None
    asset: str = ""
    base: TissueBaseState | None = None
    warning: str = ""
