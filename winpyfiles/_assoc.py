"""Windows file association management for Python scripts."""
import os
import shutil
from dataclasses import dataclass
from typing import Dict, List, Optional

from ._registry import HKCR, HKCU, HKLM, read_value, write_value

EXTENSIONS = (".py", ".pyw")


@dataclass
class ExtensionInfo:
    extension: str
    prog_id_hkcu: Optional[str]      # HKCU\Software\Classes\<ext>  (user override)
    prog_id_hklm: Optional[str]      # HKLM\SOFTWARE\Classes\<ext>  (system)
    prog_id_effective: Optional[str]  # HKCR\<ext>                   (merged, what Windows uses)


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

        ext_infos.append(ExtensionInfo(
            extension=ext,
            prog_id_hkcu=prog_id_hkcu,
            prog_id_hklm=prog_id_hklm,
            prog_id_effective=prog_id_effective,
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


def find_py_exe() -> Optional[str]:
    """Return the path to the Python Launcher (py.exe), or None if not found."""
    found = shutil.which("py")
    if found:
        return found
    default = r"C:\Windows\py.exe"
    if os.path.isfile(default):
        return default
    return None


def set_command(prog_id: str, command: str, hive: int = HKLM) -> None:
    """Write the shell open command for a ProgID into the given registry hive.

    Requires administrator rights when hive is HKLM (the default).
    """
    prefix = "SOFTWARE\\Classes" if hive == HKLM else "Software\\Classes"
    write_value(hive, f"{prefix}\\{prog_id}\\shell\\open\\command", command)


def set_prog_id(extension: str, prog_id: str, hive: int = HKLM) -> None:
    """Map a file extension to a ProgID in the given registry hive.

    Requires administrator rights when hive is HKLM (the default).
    """
    prefix = "SOFTWARE\\Classes" if hive == HKLM else "Software\\Classes"
    write_value(hive, f"{prefix}\\{extension}", prog_id)
