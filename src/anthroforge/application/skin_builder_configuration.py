"""Builder-owned parameter edits and immutable applied configuration selection."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.skin import Skin
from anthroforge.core.skin_draft import BuilderConfiguration, configuration


def policy(builder: str) -> Any:
    from .skin_evaluation import BUILDERS

    if builder not in BUILDERS:
        raise ValueError(f"The selected draft builder {builder} is unavailable.")
    return BUILDERS[builder].settings


def decode(skin: Any, builder: str = "") -> Any:
    record = skin.draft_settings.configuration(builder)
    return policy(record.builder).configuration(record)


def store(skin: Any, builder: str, values: Any) -> Any:
    record = configuration(builder, asdict(values))
    return replace(skin, draft_settings=skin.draft_settings.updated(record))


def configure(skin: Any, builder: str, values: dict[str, Any]) -> Any:
    selected = policy(builder)
    current = decode(skin, builder)
    return store(skin, builder, selected.configure(current, values))


def contributor(skin: Any, owner: str, values: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
    from .skin_evaluation import BUILDERS

    remaining = dict(values)
    for key, builder in BUILDERS.items():
        selected = builder.settings
        changes = {k: remaining.pop(k) for k in selected.contributor_fields if k in remaining}
        if changes:
            current = decode(skin, key)
            skin = store(skin, key, selected.configure_contributor(current, owner, changes))
    return skin, remaining


def settings_for(skin: Any, owner: str, builder: str = "") -> Any:
    selected = policy(builder or skin.draft_settings.backend)
    return selected.contributor(decode(skin, builder), owner)


def effective(skin: Any, owner: str, name: str) -> Any:
    selected = policy(skin.draft_settings.backend)
    config = decode(skin)
    return selected.effective(config, selected.contributor(config, owner), name)


def automatic(skin: Skin) -> BuilderConfiguration:
    if skin.applied_draft is not None:
        return skin.applied_draft.configuration
    return skin.migration_draft or skin.draft_settings.configuration()


def projected(document: Any, config: BuilderConfiguration) -> Any:
    settings = document.skin.draft_settings.updated(config)
    skin = replace(document.skin, draft_settings=replace(settings, backend=config.builder))
    return document if skin == document.skin else replace(document, skin=skin)


def retained(skin: Any) -> set[str]:
    from .skin_evaluation import BUILDERS

    records = list(skin.draft_settings.configurations)
    records += [skin.applied_draft.configuration] if skin.applied_draft else []
    records += [skin.migration_draft] if skin.migration_draft else []
    return set().union(
        *(BUILDERS[r.builder].settings.resources(r) for r in records if r.builder in BUILDERS)
    )
