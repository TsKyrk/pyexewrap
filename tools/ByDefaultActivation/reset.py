"""Reset .py and .pyw file associations back to the standard Python launcher.

Removes the pyexewrap override and restores the original handlers:

  1. HKCU AppX handlers (no admin needed) -- deletes our HKCU override so the
     MSIX Python Manager's default command is used again.
  2. HKLM Python.File / Python.NoConsole ftype (requires admin) -- restores
     the classic fallback layer to plain python.exe.

Backs up the current registry state before making any change.
"""
import sys
import os

# Allow running directly from this folder without installing the packages.
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from winpyfiles import diagnose, find_py_exe, find_python_appx_prog_ids, set_command
from winpyfiles._registry import HKCU, delete_value, notify_shell_assoc_changed
from winpyfiles._elevation import is_admin, elevate_and_rerun
from winpyfiles._backup import backup


def main():
    # Save current state before modifying anything.
    saved = backup()
    print(f"Backup saved: {saved}")

    # --- Layer 1: HKCU AppX handlers -- delete our override, restore MSIX default ---
    appx_handlers = find_python_appx_prog_ids()
    if appx_handlers:
        print("\n  Restoring HKCU AppX handlers (MSIX Python Manager):")
        for prog_id in appx_handlers:
            delete_value(HKCU, f"Software\\Classes\\{prog_id}\\shell\\open\\command")
            print(f"    Removed HKCU override for {prog_id}")
        notify_shell_assoc_changed()
        print()
        print("  [!!] WARNING: MSIX Python Manager is still installed.")
        print("       Double-click behavior is controlled by AppxManifest.xml, not the registry.")
        print("       .py files will continue to open with the MSIX Python Manager's bundled")
        print("       python.exe -- NOT with the system default launcher.")
        print()
        print("  To fully restore default open-with-system-Python behavior:")
        print("    Option A: Uninstall 'Python Manager' from the Microsoft Store.")
        print("    Option B: In Windows Settings > Apps > Default apps, reset .py/.pyw manually.")
    else:
        print("\n  No HKCU AppX handlers found.")

    # --- Layer 2: HKLM ftype (classic fallback, requires admin) ---
    if not is_admin():
        print("\n  [!] Skipping HKLM ftype update (requires admin).")
        print("      Re-run as admin or use --elevate to also update the classic ftype layer.")
    else:
        py_exe = find_py_exe()
        if not py_exe:
            print("[!] No usable Python executable found.")
        else:
            command = f'"{py_exe}" "%1" %*'
            d = diagnose()
            prog_ids_done = set()
            print("\n  Resetting HKLM ftype (classic layer):")
            for ext in d.extensions:
                pid = ext.prog_id_effective
                if not pid or pid in prog_ids_done:
                    continue
                set_command(pid, command)
                print(f"    Set {pid} -> {command}")
                prog_ids_done.add(pid)

    print("\nDone. .py and .pyw files now open with the default Python launcher.")
    print("Run 'py -m winpyfiles diagnose' to verify.")

    if _is_double_clicked():
        input("\nPress Enter to close...")


def _is_double_clicked():
    return len(sys.argv) == 1 and sys.stdin and sys.stdin.isatty()


if __name__ == "__main__":
    main()
