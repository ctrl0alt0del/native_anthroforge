"""Worker-owned skin stage bundles, independent of publication and editor state."""

from dataclasses import dataclass

from anthroforge.native.mesh import Mesh

from .skin_assets import SkinAsset


@dataclass(frozen=True)
class ComputedStage:
    mesh: Mesh
    data: SkinAsset
    reference: SkinAsset | None = None
    sources: tuple[str, ...] = ()


class IncompleteBuild(Exception):
    def __init__(self, stages: dict[str, ComputedStage], error: Exception):
        super().__init__(str(error))
        self.stages = stages
