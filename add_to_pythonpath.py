"""
Adds the root of this repository to the system-wide PYTHONPATH environment variable,
so you can `import pyexewrap` from anywhere without installing the package.

Usage: double-click this file, or run it from any terminal:
    python add_to_pythonpath.py

How it works:
    Writes directly to the Windows registry
    (HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment)
    and broadcasts WM_SETTINGCHANGE so the change takes effect in new terminals
    without requiring a reboot.

Alternatively, you can add the path manually:

  - Windows GUI (recommended):
      Desktop > Properties > Advanced settings > Environment variables...
      Add the path to the repo root in the "PYTHONPATH" system variable.

  - PowerShell (run as admin):
      $pyexewrap_path = "C:\\your\\path\\here\\pyexewrap"
      [Environment]::SetEnvironmentVariable("PYTHONPATH",
          [Environment]::GetEnvironmentVariable("PYTHONPATH") + ";$pyexewrap_path",
          "Machine")

  - cmd (run as admin):
      setx /M PYTHONPATH "%PYTHONPATH%;C:\\your\\path\\here\\pyexewrap"

Note: why not `pip install -e .` ?
    pyexewrap is invoked by py.exe via a shebang line. py.exe uses the system Python,
    not a virtual environment. An editable install inside a venv would therefore not
    be visible to py.exe when launching scripts from the file explorer.
    The PYTHONPATH approach is system-wide and works regardless of the active environment.
"""

import os
import sys
import winreg
import ctypes


def _ensure_admin() -> None:
    """Re-launches the script with admin privileges if not already elevated."""
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False

    if not is_admin:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()


def add_to_pythonpath(path: str) -> None:
    """Adds 'path' to the system-wide PYTHONPATH environment variable."""

    reg_key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        R"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        0,
        winreg.KEY_READ | winreg.KEY_WRITE,
    )

    try:
        current_value, _ = winreg.QueryValueEx(reg_key, "PYTHONPATH")
    except FileNotFoundError:
        current_value = ""

    existing_paths = set(p.strip("\\").lower() for p in current_value.split(";") if p)

    if path.strip("\\").lower() in existing_paths:
        print(f"'{path}' is already in PYTHONPATH. No changes made.")
        winreg.CloseKey(reg_key)
        input("Press a key...")
        return

    new_value = f"{current_value};{path}" if current_value else path
    winreg.SetValueEx(reg_key, "PYTHONPATH", 0, winreg.REG_EXPAND_SZ, new_value)
    winreg.CloseKey(reg_key)

    # Broadcast the change so terminals pick it up without reboot
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x001A
    ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", 2, 5000, None
    )

    print("PYTHONPATH updated successfully.")
    print(f"New value: {new_value}")
    input("Press a key...")


if __name__ == "__main__":
    _ensure_admin()
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    add_to_pythonpath(parent_dir)
