"""Feedback draft evidence freezes before the modal; generation happens on delivery."""

from dataclasses import replace
from threading import Event

from anthroforge.application import inspection_report, report_archive
from anthroforge.feedback.attachments import materialize

from .feedback_paint import prepare


def capture(controller):
    if controller.session.shortcut_comparison.baseline is None:
        return None
    options = controller.inspection_export.options("")
    options.pop("path")
    options.pop("comparison", None)
    options.pop("replay", None)
    frozen = inspection_report.capture(controller.session, **options)
    return inspection_report.comparison_options(controller.session, frozen, True, True)


def prepare_report(report, image, frozen, included, replay):
    prepared = prepare(report, image)
    if not included or frozen is None:
        return prepared
    value = replace(frozen, comparison=replace(frozen.comparison, replay=replay))
    def writer(path):
        return report_archive.write(path, value, inspection_report.metadata(value), Event())
    attachment = materialize("comparison.afinspection.zip", writer)
    return replace(prepared, files=(attachment,))
