"""The single composition point for interchangeable draft builders."""

from typing import Any

from anthroforge.core import skin_avbd_settings, skin_field
from anthroforge.core.skin_draft import BuilderConfiguration

from . import skin_avbd, skin_avbd_capture, skin_field_builder, skin_field_capture
from . import skin_avbd_configuration as avbd
from . import skin_field_configuration as field
from .skin_draft_build import BuilderSettingsPolicy, DraftBuilder


def no_resources(record: BuilderConfiguration) -> set[str]:
    return set()


def unchanged(config: Any, contributor: Any, name: str) -> Any:
    return contributor


def field_signature(document: Any) -> tuple[str, ...]:
    from anthroforge.core import skin_sources

    record = document.skin.draft_settings.configuration("FIELD")
    config = skin_field.decode(record)
    settings = {row.owner: row for row in config.contributors}
    effective = tuple(
        skin_field.effective_collagen(
            settings.get(row.owner, skin_field.FieldContributor(row.owner)),
            document.object(row.owner).name,
        )
        for row in skin_sources.contributors(document)
    )
    return repr(record), repr(effective)


FIELD_SETTINGS = BuilderSettingsPolicy(
    skin_field.decode,
    field.configure,
    field.contributor,
    field.configure_contributor,
    field.FIELDS,
    skin_field.effective,
    field.resources,
)
AVBD_SETTINGS = BuilderSettingsPolicy(
    skin_avbd_settings.decode,
    avbd.configure,
    avbd.contributor,
    avbd.configure_contributor,
    avbd.FIELDS,
    unchanged,
    no_resources,
)
BUILDERS = {
    "FIELD": DraftBuilder(
        1,
        skin_field_builder.build,
        FIELD_SETTINGS,
        field.inputs,
        skin_field_capture.capture,
        field.reason,
        field_signature,
    ),
    "AVBD": DraftBuilder(
        3,
        skin_avbd.build,
        AVBD_SETTINGS,
        avbd.inputs,
        skin_avbd_capture.capture,
        avbd.reason,
        avbd.signature,
    ),
}
