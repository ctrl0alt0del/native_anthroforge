from anthroforge.application.changes import DocumentChanges
from anthroforge.core.construction import Control
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.desktop.scene_projection import control_targets


def scene():
    root = SCP("Root", id="root")
    following = Control("Follower", "HOOK", id="follow", follow=root.id)
    attached = Control("Attached", "HOOK", id="attached", support=following.id)
    other = Control("Unrelated", "HOOK", id="other")
    return Document(entities=(root,), controls=(following, attached, other))


def test_control_projection_recomputes_only_changed_outputs_and_dependents():
    document = scene()
    changes = DocumentChanges(entities={"root": {"primitive"}})
    assert control_targets(document, changes, False) == set()
    changes = DocumentChanges(entities={"root": {"matrix"}})
    assert control_targets(document, changes, False) == {"follow", "attached"}
    changes = DocumentChanges(controls={"follow": {"matrix"}})
    assert control_targets(document, changes, False) == {"follow", "attached"}
    changes = DocumentChanges(controls={"other": {"name"}})
    assert control_targets(document, changes, False) == {"other"}


def test_relationship_edits_refresh_controls_with_removed_consumers():
    document = scene()
    changes = DocumentChanges(controls={"attached": {"support"}})
    assert control_targets(document, changes, False) == set(document.index.controls)
    assert control_targets(document, DocumentChanges(), True) == set(document.index.controls)
