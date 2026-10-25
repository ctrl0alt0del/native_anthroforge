"""Per-user registration; Windows retains ownership of the user's default-app choice."""

import ctypes
from collections.abc import Callable
from pathlib import Path

NAME = "AnthroForge"
PROGID = "AnthroForge.Project"
CLASSES = r"Software\Classes"
CAPABILITIES = r"Software\AnthroForge\Capabilities"
SETTINGS = "ms-settings:defaultapps?registeredAppUser=AnthroForge"
Entry = tuple[str, str, str]


def entries(executable: Path) -> tuple[Entry, ...]:
    executable = executable.resolve(strict=True)
    if executable.suffix.lower() != ".exe" or any(c in str(executable) for c in '"\r\n'):
        raise ValueError("Choose a packaged AnthroForge executable.")
    command, icon = f'"{executable}" --project "%1"', f'"{executable}",0'
    return (*file_entries(command, icon), *application_entries(icon))


def file_entries(command: str, icon: str) -> tuple[Entry, ...]:
    program = CLASSES + "\\" + PROGID
    application = CLASSES + r"\Applications\AnthroForge.exe"
    return (
        (program, "", "AnthroForge project"),
        (program + r"\DefaultIcon", "", icon),
        (program + r"\shell\open\command", "", command),
        (CLASSES + r"\.anthroforge\OpenWithProgids", PROGID, ""),
        (application, "FriendlyAppName", NAME),
        (application + r"\SupportedTypes", ".anthroforge", ""),
        (application + r"\shell\open\command", "", command),
    )


def application_entries(icon: str) -> tuple[Entry, ...]:
    return (
        (CAPABILITIES, "ApplicationName", NAME),
        (CAPABILITIES, "ApplicationDescription", "Create and edit anatomical models."),
        (CAPABILITIES, "ApplicationIcon", icon),
        (CAPABILITIES + r"\FileAssociations", ".anthroforge", PROGID),
        (r"Software\RegisteredApplications", NAME, CAPABILITIES),
    )


def write_value(key: str, name: str, value: str) -> None:
    import winreg

    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key, access=winreg.KEY_SET_VALUE) as handle:
        winreg.SetValueEx(handle, name, 0, winreg.REG_SZ, value)


def notify_shell() -> None:
    shell = ctypes.WinDLL("shell32")
    changed = shell.SHChangeNotify
    changed.argtypes = (ctypes.c_long, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p)
    changed.restype = None
    changed(0x08000000, 0, None, None)  # SHCNE_ASSOCCHANGED / SHCNF_IDLIST


def register(
    executable: Path,
    writer: Callable[[str, str, str], None] = write_value,
    notify: Callable[[], None] = notify_shell,
) -> str:
    for entry in entries(executable):
        writer(*entry)
    notify()
    return SETTINGS
