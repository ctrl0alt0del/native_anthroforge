"""Worker-owned skin stage bundles, independent of publication and editor state."""

from dataclasses import dataclass

from anthroforge.native.mesh import Mesh

from .skin_assets import SkinAsset


@dataclass(frozen=True)
class ComputedStage:
    mesh: Mesh
    data: SkinAsset
