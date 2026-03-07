"""Windows file association management for Python scripts."""
import os
import shutil
from dataclasses import dataclass
from typing import Dict, List, Optional

from ._registry import HKCR, HKCU, HKLM, read_value, write_value, notify_shell_assoc_changed

EXTENSIONS = (".py", ".pyw")


@dataclass
class ExtensionInfo:
    extension: str
    prog_id_hkcu: Optional[str]       # HKCU\Software\Classes\<ext>  (user override)
    prog_id_hklm: Optional[str]       # HKLM\SOFTWARE\Classes\<ext>  (system)
    prog_id_effective: Optional[str]  # HKCR\<ext>                   (merged, what Windows uses)
    user_choice: Optional[str] = None  # HKCU\...\Explorer\FileExts\<ext>\UserChoice  (Windows 8+, Explorer priority)


@dataclass
class ProgIdInfo:
    prog_id: str
    command_hkcu: Optional[str]      # HKCU\Software\Classes\<id>\shell\open\command
    command_hklm: Optional[str]      # HKLM\SOFTWARE\Classes\<id>\shell\open\command
    command_effective: Optional[str]  # HKCR\<id>\shell\open\command  (what Windows uses)


@dataclass
class AssocDiagnosis:
    extensions: List[ExtensionInfo]
    prog_ids: Dict[str, ProgIdInfo]


def diagnose() -> AssocDiagnosis:
    """Read the current Windows file associations for Python extensions."""
    ext_infos: List[ExtensionInfo] = []
    all_prog_ids: set = set()

    for ext in EXTENSIONS:
        prog_id_hkcu = read_value(HKCU, f"Software\\Classes\\{ext}")
        prog_id_hklm = read_value(HKLM, f"SOFTWARE\\Classes\\{ext}")
        prog_id_effective = read_value(HKCR, ext)
        user_choice = read_value(
            HKCU,
            f"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\{ext}\\UserChoice",
            value_name="ProgId",
        )

        ext_infos.append(ExtensionInfo(
            extension=ext,
            prog_id_hkcu=prog_id_hkcu,
            prog_id_hklm=prog_id_hklm,
            prog_id_effective=prog_id_effective,
            user_choice=user_choice,
        ))

        for pid in (prog_id_hkcu, prog_id_hklm, prog_id_effective):
            if pid:
                all_prog_ids.add(pid)

    prog_id_infos: Dict[str, ProgIdInfo] = {}
    for prog_id in sorted(all_prog_ids):
        cmd_subkey = f"{prog_id}\\shell\\open\\command"
        prog_id_infos[prog_id] = ProgIdInfo(
            prog_id=prog_id,
            command_hkcu=read_value(HKCU, f"Software\\Classes\\{cmd_subkey}"),
            command_hklm=read_value(HKLM, f"SOFTWARE\\Classes\\{cmd_subkey}"),
            command_effective=read_value(HKCR, cmd_subkey),
        )

    return AssocDiagnosis(extensions=ext_infos, prog_ids=prog_id_infos)


def _is_app_execution_alias(path: str) -> bool:
    """Return True if the path is a Windows App Execution Alias stub (not a real exe).

    Windows 10/11 creates lightweight stub executables under
    C:\\Users\\<user>\\AppData\\Local\\Microsoft\\WindowsApps\\ for apps installed
    via the Microsoft Store or MSIX packages (including modern Python installs).

    These stubs work fine when invoked interactively (e.g. typing "py" in a terminal),
    but FAIL SILENTLY when Windows invokes them from an ftype/shell\\open\\command
    registry entry. Explorer uses a different execution context that does not
    activate the App Execution Alias infrastructure.

    Concretely: shutil.which("py") may return the WindowsApps stub, but writing
    that path into the registry ftype command results in a no-op when double-clicking
    a .py file -- the script runs via a fallback mechanism that bypasses pyexewrap.
    """
    return "\\WindowsApps\\" in path


def find_py_exe() -> Optional[str]:
    """Return a usable Python executable for ftype/registry shell commands.

    Tries, in order:
      1. py.exe launcher via PATH -- but only if it is a real executable,
         not a Windows App Execution Alias stub (see _is_app_execution_alias).
      2. C:\\Windows\\py.exe -- the classic location from the Python installer.
      3. sys.executable -- the interpreter currently running this code, which
         is always a real python.exe (never an alias stub).

    The returned path is safe to embed in a registry shell\\open\\command string.
    """
    # Try the py launcher first, but skip App Execution Aliases.
    found = shutil.which("py")
    if found and not _is_app_execution_alias(found):
        return found

    # Known real location from classic Python installer.
    default = r"C:\Windows\py.exe"
    if os.path.isfile(default):
        return default

    # Fall back to the current interpreter (always a real python.exe).
    import sys
    if os.path.isfile(sys.executable) and not _is_app_execution_alias(sys.executable):
        return sys.executable

    return None


def set_command(prog_id: str, command: str, hive: int = HKLM) -> None:
    """Write the shell open command for a ProgID into the given registry hive.

    Requires administrator rights when hive is HKLM (the default).
    Notifies Explorer of the change so it drops its cached association.
    """
    prefix = "SOFTWARE\\Classes" if hive == HKLM else "Software\\Classes"
    write_value(hive, f"{prefix}\\{prog_id}\\shell\\open\\command", command)
    notify_shell_assoc_changed()


def set_prog_id(extension: str, prog_id: str, hive: int = HKLM) -> None:
    """Map a file extension to a ProgID in the given registry hive.

    Requires administrator rights when hive is HKLM (the default).
    Notifies Explorer of the change so it drops its cached association.
    """
    prefix = "SOFTWARE\\Classes" if hive == HKLM else "Software\\Classes"
    write_value(hive, f"{prefix}\\{extension}", prog_id)
    notify_shell_assoc_changed()
