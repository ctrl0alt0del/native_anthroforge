from unittest.mock import Mock

import pytest

from anthroforge.desktop import windows_associations as associations


def executable(tmp_path, folder="Portable app"):
    target = tmp_path / folder / "AnthroForge.exe"
    target.parent.mkdir()
    target.touch()
    return target


def test_registration_quotes_program_and_project_without_changing_default(tmp_path):
    target = executable(tmp_path)
    writes, notifications = [], []
    result = associations.register(
        target, lambda *row: writes.append(row), lambda: notifications.append(1)
    )
    commands = [value for key, name, value in writes if key.endswith(r"shell\open\command")]
    assert commands == [f'"{target}" --project "%1"'] * 2
    assert all("UserChoice" not in key for key, _, _ in writes)
    assert not any(key.endswith(r"\.anthroforge") and not name for key, name, _ in writes)
    assert (r"Software\RegisteredApplications", "AnthroForge", associations.CAPABILITIES) in writes
    assert notifications == [1] and result == associations.SETTINGS


def test_registration_relocates_own_commands_and_preserves_unrelated_values(tmp_path):
    registry = {("Unrelated", "Default"): "Other application"}

    def writer(key, name, value):
        registry[(key, name)] = value

    associations.register(executable(tmp_path), writer, lambda: None)
    relocated = executable(tmp_path, "Moved app")
    associations.register(relocated, writer, lambda: None)
    assert registry[("Unrelated", "Default")] == "Other application"
    assert (
        registry[(associations.CLASSES + r"\AnthroForge.Project\shell\open\command", "")]
        == f'"{relocated}" --project "%1"'
    )


def test_registration_error_does_not_notify_shell(tmp_path):
    writer, notifier = Mock(side_effect=PermissionError("Registration denied")), Mock()
    with pytest.raises(PermissionError, match="Registration denied"):
        associations.register(executable(tmp_path), writer, notifier)
    notifier.assert_not_called()


def test_invalid_program_does_not_write_registry(tmp_path):
    target = tmp_path / "source.py"
    target.touch()
    writer = Mock()
    with pytest.raises(ValueError, match="packaged"):
        associations.register(target, writer, Mock())
    writer.assert_not_called()


def test_missing_program_does_not_write_registry(tmp_path):
    writer = Mock()
    with pytest.raises(FileNotFoundError):
        associations.register(tmp_path / "removed.exe", writer, Mock())
    writer.assert_not_called()
