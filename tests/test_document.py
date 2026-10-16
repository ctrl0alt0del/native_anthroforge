import dataclasses
import json

import pytest

from anthroforge.application.session import Session
from anthroforge.core.document import Document


def test_empty_document_is_valid_and_serializable():
    session = Session("Head")
    record = json.loads(json.dumps(session.describe()))
    assert record["name"] == "Head"
    assert record["metres_per_unit"] == 1.0
    assert record["entity_count"] == 0
    assert record["skin_available"] is False


def test_documents_have_independent_identities():
    assert Session().document.id != Session().document.id


def test_document_is_immutable():
    with pytest.raises(dataclasses.FrozenInstanceError):
        Document().name = "Changed"


@pytest.mark.parametrize("name", ["", "  ", "\t"])
def test_empty_names_are_rejected(name):
    with pytest.raises(ValueError, match="name"):
        Session(name)


def test_negative_revision_is_rejected():
    with pytest.raises(ValueError, match="revision"):
        Document(revision=-1)
