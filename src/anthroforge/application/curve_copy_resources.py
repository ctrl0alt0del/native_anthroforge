"""Copy definition identities and immutable resource metadata once for the whole copied set."""

from dataclasses import dataclass, field, replace
from typing import Any
from uuid import uuid4

from anthroforge.core.construction import Curve
from anthroforge.core.fibers import Fiber

from . import curve_copy


@dataclass
class Copies:
    resources: Any
    identities: dict[str, str]
    paths: dict[str, str] = field(default_factory=dict)
    attachments: dict[str, str] = field(default_factory=dict)

    def definition(self, item: Curve) -> Curve:
        for key in (item.id, *(p.id for p in item.points)):
            if key not in self.identities:
                self.identities[key] = str(uuid4())
        copied = curve_copy.clone(item, self.identities)
        if isinstance(copied, Fiber):
            edit = copied.edit
            if edit:
                edit = replace(edit, baseline=self.path(edit.baseline))
            copied = replace(
                copied, edit=edit, attachment_asset=self.attachment(copied.attachment_asset)
            )
        return copied

    def record(self, item: Curve) -> Curve:
        from .construction_copy import remap_result

        copied = self.definition(item)
        result = remap_result(item.result, self.identities)
        return replace(
            copied,
            generation=item.generation,
            pose_revision=item.pose_revision,
            construction_revision=item.construction_revision,
            result=replace(result, asset=self.path(result.asset)),
        )

    def path(self, key: str) -> str:
        if not key or key in self.paths:
            return self.paths.get(key, "")
        source = self.resources.paths[key]
        copied = self.definition(source.authored)
        new = self.paths[key] = str(uuid4())
        self.resources.paths[new] = replace(source, authored=copied)
        return new

    def attachment(self, key: str) -> str:
        if not key or key in self.attachments:
            return self.attachments.get(key, "")
        source = self.resources.attachments[key]
        targets = tuple(self.identities.get(k, k) for k in source.targets)
        new = self.attachments[key] = str(uuid4())
        self.resources.attachments[new] = replace(source, targets=targets)
        return new
