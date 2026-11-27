"""Migration and serialization of builder-owned authored and accepted configurations."""

from dataclasses import asdict
from typing import Any

from anthroforge.core import skin_avbd_settings, skin_field
from anthroforge.core.skin_draft import (
    AppliedDraftConfiguration,
    BuilderConfiguration,
    DraftSettings,
)
from anthroforge.core.skin_draft import configuration as configured


def record(value: dict[str, Any]) -> BuilderConfiguration:
    data = dict(value)
    parameters = data.get("parameters", {})
    if isinstance(parameters, dict):
        return configured(data["builder"], parameters)
    return BuilderConfiguration(**data)


def encoded_record(value: BuilderConfiguration) -> dict[str, Any]:
    return dict(builder=value.builder, parameters=value.values())


def applied(value: dict[str, Any] | None) -> AppliedDraftConfiguration | None:
    if value is None:
        return None
    return AppliedDraftConfiguration(record(value["configuration"]), value["builder_version"])


def legacy_rows(rows: Any, cls: Any) -> list[dict[str, Any]]:
    names = cls.__dataclass_fields__.keys()
    return [{key: value for key, value in row.items() if key in names} for row in rows]


def settings(data: dict[str, Any]) -> DraftSettings:
    values = dict(data.get("draft_settings", {}))
    rows = tuple(record(row) for row in values.pop("configurations", ()))
    plan = values.pop("plan", None)
    result = DraftSettings(configurations=rows, **values)
    if "envelope_settings" in data:
        fields = legacy_rows(data.get("contributors", ()), skin_field.FieldContributor)
        value = dict(settings=data["envelope_settings"], contributors=fields)
        result = result.updated(configured("FIELD", value))
    if plan is not None or any("build_mode" in r for r in data.get("contributors", ())):
        avbd = legacy_rows(data.get("contributors", ()), skin_avbd_settings.AvbdContributor)
        result = result.updated(configured("AVBD", dict(plan=plan or "{}", contributors=avbd)))
    return result


def upgrade(data: dict[str, Any]) -> dict[str, Any]:
    draft = settings(data)
    migration = data.get("migration_draft")
    legacy = "applied_draft" not in data and data.get("envelope", {}).get("asset")
    baseline = draft.configuration() if legacy else None
    return dict(
        draft_settings=draft,
        applied_draft=applied(data.get("applied_draft")),
        migration_draft=record(migration) if migration else baseline,
    )


def encode(skin: Any) -> dict[str, Any]:
    data = asdict(skin)
    data["draft_settings"]["configurations"] = [
        encoded_record(r) for r in skin.draft_settings.configurations
    ]
    if skin.applied_draft:
        data["applied_draft"]["configuration"] = encoded_record(skin.applied_draft.configuration)
    if skin.migration_draft:
        data["migration_draft"] = encoded_record(skin.migration_draft)
    return data
