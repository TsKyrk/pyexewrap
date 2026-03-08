"""Unregister pyexewrap as a Windows application for .py and .pyw files.

Undoes all changes made by register.py:
  - Removes the pyexewrap.PyFile ProgID from HKCU\Software\Classes
  - Removes the Applications\pyexewrap entry
  - Removes the RegisteredApplications entry and Capabilities
  - Removes pyexewrap.PyFile from OpenWithProgids for .py and .pyw
"""
import sys
import os
import winreg

_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from winpyfiles._registry import HKCU, notify_shell_assoc_changed
from winpyfiles._backup import backup

PROG_ID = "pyexewrap.PyFile"
APP_KEY = "pyexewrap"
EXTENSIONS = (".py", ".pyw")


def _delete_key_tree(hive, key_path):
    """Recursively delete a registry key and all its subkeys."""
    try:
        with winreg.OpenKey(hive, key_path, access=winreg.KEY_READ | winreg.KEY_WRITE) as key:
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, 0)
                    _delete_key_tree(hive, f"{key_path}\\{subkey_name}")
                except OSError:
                    break
        winreg.DeleteKey(hive, key_path)
    except FileNotFoundError:
        pass  # already absent


def _delete_value(hive, key_path, value_name):
    """Delete a single registry value, ignoring errors if absent."""
    try:
        with winreg.OpenKey(hive, key_path, access=winreg.KEY_WRITE) as key:
            winreg.DeleteValue(key, value_name)
    except FileNotFoundError:
        pass


def unregister():
    saved = backup()
    print(f"Backup saved: {saved}\n")

    # 1. Remove ProgID: pyexewrap.PyFile
    _delete_key_tree(HKCU, f"Software\\Classes\\{PROG_ID}")
    print(f"  [OK] Removed ProgID: {PROG_ID}")

    # 2. Remove Applications\pyexewrap
    _delete_key_tree(HKCU, f"Software\\Classes\\Applications\\{APP_KEY}")
    print(f"  [OK] Removed Applications\\{APP_KEY}")

    # 3. Remove RegisteredApplications entry and Capabilities
    _delete_value(HKCU, "Software\\RegisteredApplications", APP_KEY)
    _delete_key_tree(HKCU, f"Software\\{APP_KEY}")
    print(f"  [OK] Removed RegisteredApplications entry and Capabilities")

    # 4. Remove pyexewrap.PyFile from OpenWithProgids for each extension
    for ext in EXTENSIONS:
        _delete_value(HKCU, f"Software\\Classes\\{ext}\\OpenWithProgids", PROG_ID)
        print(f"  [OK] {ext} -> OpenWithProgids -= {PROG_ID}")

    notify_shell_assoc_changed()

    print()
    print("Done. pyexewrap has been unregistered as a Windows application.")
    print("Run 'py -m winpyfiles diagnose' to verify.")


def main():
    unregister()

    if _is_double_clicked():
        input("\nPress Enter to close...")


def _is_double_clicked():
    return len(sys.argv) == 1 and sys.stdin and sys.stdin.isatty()


if __name__ == "__main__":
    main()
