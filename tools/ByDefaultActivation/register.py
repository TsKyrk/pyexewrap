"""Register pyexewrap as a Windows application for .py and .pyw files.

After running this script, pyexewrap appears in:
  - Right-click > "Ouvrir avec" / "Open with"
  - Windows Settings > Applications > Applications par defaut > .py

The user can then set pyexewrap as the default handler by:
  Right-click a .py file > Open with > Choose another app
                         > pyexewrap > Always use this app

This sets UserChoice (the highest-priority mechanism), which works even
when the MSIX Python Manager is installed -- because UserChoice set via
the UI carries a valid hash that Windows accepts.
"""
import sys
import os
import winreg

_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from winpyfiles import find_py_exe
from winpyfiles._registry import HKCU, write_value, notify_shell_assoc_changed

PROG_ID = "pyexewrap.PyFile"
APP_KEY = "pyexewrap"
APP_DISPLAY_NAME = "pyexewrap"
APP_DESCRIPTION = "Python script launcher with automatic virtual environment activation"
EXTENSIONS = (".py", ".pyw")


def register():
    py_exe = find_py_exe()
    if not py_exe:
        print("[!] No usable Python executable found. Is Python installed?")
        sys.exit(1)

    command = f'"{py_exe}" -m pyexewrap "%1" %*'
    icon = f'"{py_exe}",0'

    print(f"Registering pyexewrap with command: {command}\n")

    # 1. ProgID: pyexewrap.PyFile
    #    Defines what Windows runs when this handler is chosen.
    write_value(HKCU, f"Software\\Classes\\{PROG_ID}", APP_DISPLAY_NAME)
    write_value(HKCU, f"Software\\Classes\\{PROG_ID}\\DefaultIcon", icon)
    write_value(HKCU, f"Software\\Classes\\{PROG_ID}\\shell\\open\\command", command)
    with winreg.CreateKeyEx(HKCU, f"Software\\Classes\\{PROG_ID}\\shell\\open",
                            access=winreg.KEY_WRITE) as k:
        winreg.SetValueEx(k, "FriendlyAppName", 0, winreg.REG_SZ, APP_DISPLAY_NAME)
    print(f"  [OK] ProgID registered: {PROG_ID}")

    # 2. Applications\pyexewrap
    #    Makes pyexewrap appear in the "Open with" context menu and dialog.
    write_value(HKCU, f"Software\\Classes\\Applications\\{APP_KEY}\\shell\\open\\command", command)
    with winreg.CreateKeyEx(HKCU, f"Software\\Classes\\Applications\\{APP_KEY}\\shell\\open",
                            access=winreg.KEY_WRITE) as k:
        winreg.SetValueEx(k, "FriendlyAppName", 0, winreg.REG_SZ, APP_DISPLAY_NAME)
    with winreg.CreateKeyEx(HKCU, f"Software\\Classes\\Applications\\{APP_KEY}\\SupportedTypes",
                            access=winreg.KEY_WRITE) as k:
        for ext in EXTENSIONS:
            winreg.SetValueEx(k, ext, 0, winreg.REG_SZ, "")
    print(f"  [OK] Applications\\{APP_KEY} registered")

    # 3. RegisteredApplications + Capabilities
    #    Makes pyexewrap appear in Settings > Apps > Applications par defaut.
    caps_path = f"Software\\{APP_KEY}\\Capabilities"
    write_value(HKCU, caps_path, APP_DISPLAY_NAME, value_name="ApplicationName")
    write_value(HKCU, caps_path, APP_DESCRIPTION, value_name="ApplicationDescription")
    with winreg.CreateKeyEx(HKCU, f"{caps_path}\\FileAssociations",
                            access=winreg.KEY_WRITE) as k:
        for ext in EXTENSIONS:
            winreg.SetValueEx(k, ext, 0, winreg.REG_SZ, PROG_ID)
    with winreg.CreateKeyEx(HKCU, "Software\\RegisteredApplications",
                            access=winreg.KEY_WRITE) as k:
        winreg.SetValueEx(k, APP_KEY, 0, winreg.REG_SZ, caps_path)
    print(f"  [OK] RegisteredApplications entry added")

    # 4. OpenWithProgids for .py and .pyw
    #    Adds the ProgID to the list of known handlers for each extension.
    for ext in EXTENSIONS:
        with winreg.CreateKeyEx(HKCU, f"Software\\Classes\\{ext}\\OpenWithProgids",
                                access=winreg.KEY_WRITE) as k:
            winreg.SetValueEx(k, PROG_ID, 0, winreg.REG_NONE, b"")
        print(f"  [OK] {ext} -> OpenWithProgids += {PROG_ID}")

    notify_shell_assoc_changed()

    print()
    print("Done. pyexewrap is now registered as a Windows application.")
    print()
    print("To set it as the default for .py files:")
    print("  Right-click a .py file > Ouvrir avec > Choisir une autre application")
    print("  > pyexewrap > Toujours utiliser cette application")
    print()
    print("Or: Parametres Windows > Applications > Applications par defaut > .py")
    print("    and select pyexewrap from the list.")
    print()
    print("Run 'py -m winpyfiles diagnose' to verify.")


def main():
    register()

    if _is_double_clicked():
        input("\nPress Enter to close...")


def _is_double_clicked():
    return len(sys.argv) == 1 and sys.stdin and sys.stdin.isatty()


if __name__ == "__main__":
    main()
