import json
from dataclasses import replace
from threading import Event, current_thread
from uuid import uuid4
from zipfile import ZipFile

import pytest

from anthroforge.feedback import storage
from anthroforge.feedback.records import Annotation, Receipt, Report
from anthroforge.feedback.service import ReportService


def example():
    return Report(
        uuid4().hex,
        "2026-10-19T12:00:00+00:00",
        "bug",
        "Unicode description: α, Україна",
        '{"application_version":"0.2.1"}',
        100,
        80,
        (Annotation("rectangle", 10, 10, 50, 40),),
        b"source-png",
        b"annotated-png",
    )


def test_local_report_portability_retry_and_collision(tmp_path):
    consumer, report = storage.LocalReportConsumer(tmp_path), example()
    receipt = consumer.submit(report)
    path = receipt.location
    assert consumer.submit(report) == receipt
    with ZipFile(path) as archive:
        data = json.loads(archive.read("report.json"))
        assert data["description"] == report.description and data["schema_version"] == 1
        assert data["annotations"][0]["kind"] == "rectangle"
        assert archive.read("original.png") == report.original_png
        assert archive.read("annotated.png") == report.annotated_png
    with pytest.raises(ValueError, match="different report"):
        consumer.submit(replace(report, description="Changed payload"))
    assert len(list(tmp_path.iterdir())) == 1


def test_publication_failure_leaves_no_partial_report(tmp_path, monkeypatch):
    def fail(*args):
        raise OSError("Disk unavailable")

    monkeypatch.setattr(storage.os, "link", fail)
    with pytest.raises(OSError, match="Disk unavailable"):
        storage.LocalReportConsumer(tmp_path).submit(example())
    assert not list(tmp_path.iterdir())


class Consumer:
    description = "Test destination"

    def __init__(self):
        self.reports, self.threads = [], []
        self.entered, self.release = Event(), Event()

    def submit(self, report):
        self.threads.append(current_thread().name)
        self.entered.set()
        assert self.release.wait(5)
        self.reports.append(report)
        return Receipt("test://reports/" + report.id, "https://example.test/report")


def test_replaceable_consumer_and_single_delivery():
    consumer, report = Consumer(), example()
    service = ReportService(consumer)
    try:
        service.start(lambda: report)
        assert consumer.entered.wait(5)
        with pytest.raises(ValueError, match="already"):
            service.start(lambda: report)
        consumer.release.set()
        assert service.future.result(5).location.endswith(report.id)
        assert service.poll() and service.state == "saved"
        assert consumer.reports == [report] and consumer.threads[0].startswith("feedback")
    finally:
        consumer.release.set()
        service.close()


def test_failed_preparation_can_retry_same_report(tmp_path):
    service, report = ReportService(storage.LocalReportConsumer(tmp_path)), example()
    try:
        service.start(lambda: (_ for _ in ()).throw(ValueError("Encoding failed")))
        with pytest.raises(ValueError):
            service.future.result(5)
        assert service.poll() and service.state == "failed" and service.error == "Encoding failed"
        service.start(lambda: report)
        service.future.result(5)
        assert service.poll() and service.state == "saved"
        assert len(list(tmp_path.glob("*.afreport.zip"))) == 1
    finally:
        service.close()


def test_inbox_does_not_depend_on_installation(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "user"))
    monkeypatch.chdir(tmp_path)
    assert storage.default_directory() == tmp_path / "user/AnthroForge/Reports"
