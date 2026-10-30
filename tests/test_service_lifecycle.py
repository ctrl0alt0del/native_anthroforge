"""Context lifecycle ordering, teardown and project replacement contracts."""

from dataclasses import replace

import pytest

from anthroforge.application import projects
from anthroforge.application.resources import Resources
from anthroforge.application.service_lifecycle import Event, Lifecycle, Service
from anthroforge.application.session import Session
from anthroforge.core.document import Document


def test_subscriptions_are_explicit_and_close_is_idempotent():
    lifecycle, events = Lifecycle(), []
    service = Service("observed", ((Event.CLOSE, lambda: events.append("close")),))
    lifecycle.register(service)
    with pytest.raises(ValueError, match="Cannot register"):
        lifecycle.register(service)
    lifecycle.close()
    lifecycle.close()
    lifecycle.emit(Event.CLOSE)
    assert events == ["close"] and not lifecycle.hooks


def fail_close():
    raise ValueError("cleanup failure")


def test_teardown_releases_other_services_after_failure():
    lifecycle, events = Lifecycle(), []
    lifecycle.register(Service("failed", ((Event.CLOSE, fail_close),)))
    lifecycle.register(Service("remaining", ((Event.CLOSE, lambda: events.append("released")),)))
    with pytest.raises(ExceptionGroup, match="cleanup"):
        lifecycle.close()
    assert events == ["released"] and lifecycle.closed
    lifecycle.close()


def test_project_replacement_releases_old_context_and_keeps_status_subscription():
    session, notifications = Session(), []
    old = session.services
    session.skin_status.subscribe(lambda: notifications.append(session.document.name))
    try:
        projects.adopt(session, Document(name="Replacement"), Resources())
        assert old.closed and session.services is not old
        session.document = replace(session.document, name="Changed")
        assert notifications[-1] == "Changed"
        assert not session.issues.listening.closed
    finally:
        session.close()


def test_context_services_receive_only_their_own_document_changes():
    session, events = Session(), []
    try:
        session.contexts.add("candidate", Document(name="Candidate"))
        session.skin_status.subscribe(lambda: events.append("root"))
        with session.contexts.use("candidate"):
            session.skin_status.subscribe(lambda: events.append("candidate"))
            session.document = replace(session.document, name="Candidate changed")
        assert events == ["candidate"]
        session.document = replace(session.document, name="Root changed")
        assert events == ["candidate", "root"]
    finally:
        session.close()
