"""RFC 6901 subtree literals preserve all existing result-reference requests."""

import pytest

from anthroforge import authoring, authoring_arguments


def test_literal_name_and_resolved_parent_share_one_request(session):
    root = session.command("scp.empty", name="Root")
    result = authoring.dispatch(
        session,
        dict(
            operation="scp.empty",
            arguments=dict(name="$pelvis", parent="$root"),
            literal_paths=["/name"],
        ),
        {"root": root},
    )
    item = session.document.entity(result["result"])
    assert item.name == "$pelvis" and item.parent == root


def test_literals_select_subtrees_and_escaped_tokens():
    data = {"a/b": {"~field": ["$missing", {"value": "$missing.again"}]}, "ref": "$a.0.id"}
    request = dict(arguments=data, literal_paths=["/a~1b/~0field"])
    result = authoring_arguments.arguments(request, {"a": [dict(id="resolved")]})
    assert result["a/b"] == data["a/b"] and result["ref"] == "resolved"
    assert data["ref"] == "$a.0.id"


def test_empty_pointer_and_empty_key_are_distinct():
    data = {"": "$name", "other": "$value"}
    assert authoring_arguments.arguments(dict(arguments=data, literal_paths=[""]), {}) == data
    result = authoring_arguments.arguments(dict(arguments=data, literal_paths=["/"]), {"value": 3})
    assert result == {"": "$name", "other": 3}


@pytest.mark.parametrize(
    "pointer", ["name", "#/name", "/na~2me", "/name~", "/missing", "/name/child"]
)
def test_bad_pointer_rejected_before_application_command(session, pointer):
    before, cursor = session.document, session.history.cursor
    result = authoring.response(
        session,
        dict(operation="scp.empty", arguments=dict(name="Test"), literal_paths=[pointer]),
        {},
    )
    assert not result["ok"] and "literal_paths" in result["error"]
    assert session.document is before and session.history.cursor == cursor


@pytest.mark.parametrize("pointer", ["/values/-", "/values/-1", "/values/01", "/values/1"])
def test_json_pointer_array_indices_are_canonical_and_existing(pointer):
    with pytest.raises(ValueError, match="missing argument"):
        authoring_arguments.arguments(
            dict(arguments={"values": ["$literal"]}, literal_paths=[pointer]), {}
        )


def test_mixed_array_literals_and_reference_errors_report_argument_location():
    request = dict(arguments={"values": ["$literal", "$data.answer"]}, literal_paths=["/values/0"])
    assert authoring_arguments.arguments(request, {"data": dict(answer=42)})["values"] == [
        "$literal",
        42,
    ]
    with pytest.raises(ValueError, match=r"arguments/values/1.*literal_paths"):
        authoring_arguments.arguments(request, {})


@pytest.mark.parametrize("paths", [None, "/name", [False], [4]])
def test_literal_paths_requires_string_array(paths):
    with pytest.raises(ValueError, match="array"):
        authoring_arguments.arguments(dict(literal_paths=paths), {})


def test_nested_dictionary_payload_is_not_reserved_or_reinterpreted():
    data = {"data": {"literal": "$text"}, "value": "$known"}
    result = authoring_arguments.arguments(
        dict(arguments=data, literal_paths=["/data"]), {"known": 7}
    )
    assert result == {"data": {"literal": "$text"}, "value": 7}
