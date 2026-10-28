from dataclasses import replace

import pytest

from anthroforge.application.skeleton_matching import inventory, parse
from anthroforge.core.assembly import ImportProvenance
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.skeleton_update import Finding, require_review


def skeleton():
    return Document(entities=(SCP("Bone", id="bone"),))


def test_names_do_not_match_independent_skeletons():
    source, destination = skeleton(), skeleton()
    assert inventory(source, destination)[0]["suggested"] == ""
    assert inventory(source, replace(source, name="Copy"))[0]["suggested"] == "bone"


def test_shared_import_provenance_matches_independently_copied_skeletons():
    original = skeleton()
    receipt = ImportProvenance("import", str(original.id), 1, "hash", "Source", (("bone", "copy"),))
    copied = Document(entities=(SCP("Renamed", id="copy"),), imports=(receipt,))
    assert inventory(original, copied)[0]["suggested"] == "copy"
    assert inventory(copied, original)[0]["suggested"] == "bone"


def test_ambiguous_import_provenance_remains_unselected():
    original = skeleton()
    receipt = ImportProvenance(
        "import", str(original.id), 1, "hash", "Source", (("bone", "a"), ("bone", "b"))
    )
    copied = Document(
        entities=(SCP("Root", id="a"), SCP("Other", id="b", parent="a")), imports=(receipt,)
    )
    assert inventory(original, copied)[0]["suggested"] == ""
    assert inventory(original, copied)[0]["candidates"] == ("a", "b")


def test_matches_are_one_to_one_and_require_existing_scps():
    source = Document(entities=(SCP("Root", id="a"), SCP("Other", id="b", parent="a")))
    destination = skeleton()
    with pytest.raises(ValueError, match="one-to-one"):
        parse(source, destination, {"a": "bone", "b": "bone"})
    with pytest.raises(ValueError):
        parse(source, destination, {"unknown": "bone"})


def test_apply_acknowledges_exact_current_findings_only():
    findings = (Finding("rebind:a", "a", "New attachment", acknowledge=True),)
    require_review(findings, ["rebind:a"])
    with pytest.raises(ValueError, match="Acknowledge"):
        require_review(findings, [])
    with pytest.raises(ValueError, match="Resolve"):
        require_review((Finding("invalid", "a", "Invalid bone", blocking=True),), ["invalid"])
