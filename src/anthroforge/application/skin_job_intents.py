"""Captured skin intent is independent of pending settings and later UI changes."""

from dataclasses import dataclass
from typing import Any

from anthroforge.core.jobs import ObsoleteInputs
from anthroforge.core.results import Port
from anthroforge.core.skin_draft import BuilderConfiguration

from . import skin_builder_configuration as builders


@dataclass(frozen=True)
class Intent:
    configuration: BuilderConfiguration
    epoch: int
    automatic: bool = False

    def project(self, document: Any) -> Any:
        return builders.projected(document, self.configuration)


def capture(session: Any, stage: str, automatic: bool = False, config: Any = None) -> Intent:
    skin = session.document.skin
    selected = skin.draft_settings.configuration()
    config = config or (
        selected if stage in ("envelope", "construction") else builders.automatic(skin)
    )
    return Intent(config, session.skin_pipeline.epoch, automatic)


def require(session: Any, intent: Intent, stage: str) -> None:
    if intent.epoch != session.skin_pipeline.epoch:
        raise ObsoleteInputs("Skin target intent changed before publication.")
    if stage != "envelope" and session.document.skin.update_mode != "FINAL":
        raise ObsoleteInputs("Final pipeline work is no longer requested.")


def prepare(session: Any, intent: Intent, stage: str, document: Any) -> tuple[Any, Any, Any]:
    require(session, intent, stage)
    return intent.project(document), session.resources.snapshot(), session.preferences.value


def inputs(intent: Intent, policy: Any, document: Any) -> Any:
    ports = policy.inputs(intent.project(document))
    if "topology" in policy.outputs or "final" in policy.outputs:
        ports.add(Port(str(document.id), "skin_update_mode"))
    return ports
