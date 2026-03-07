"""Activate pyexewrap as the default handler for .py and .pyw files.

On systems with the MSIX Python Manager/Launcher (installed from the Microsoft
Store or via a modern Python installer), double-clicks on .py files are handled
by AppX ProgIDs registered in HKCU -- these take priority over the traditional
HKLM ftype mechanism. This script patches both layers:

  1. HKCU AppX handlers (no admin needed) -- the ones actually used by Explorer
  2. HKLM Python.File / Python.NoConsole ftype (requires admin) -- fallback layer

Backs up the current registry state before making any change.
"""
import sys
import os

# Allow running directly from this folder without installing the packages.
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from winpyfiles import diagnose, find_py_exe, find_python_appx_prog_ids, set_command
from winpyfiles._registry import HKCU
from winpyfiles._elevation import is_admin, elevate_and_rerun
from winpyfiles._backup import backup


def main():
    py_exe = find_py_exe()
    if not py_exe:
        print("[!] No usable Python executable found. Is Python installed?")
        sys.exit(1)

    # Save current state before modifying anything.
    saved = backup()
    print(f"Backup saved: {saved}")

    command = f'"{py_exe}" -m pyexewrap "%1" %*'

    # --- Layer 1: HKCU AppX handlers (used by Explorer on MSIX Python systems) ---
    # These take priority over HKLM ftype and require no admin rights.
    appx_handlers = find_python_appx_prog_ids()
    if appx_handlers:
        print("\n  Patching HKCU AppX handlers (MSIX Python Manager):")
        for prog_id, original_cmd in appx_handlers.items():
            set_command(prog_id, command, hive=HKCU)
            print(f"    {prog_id}")
            print(f"      was : {original_cmd}")
            print(f"      now : {command}")
        print()
        print("  [!!] WARNING: MSIX Python Manager detected.")
        print("       Windows activates AppX handlers via the App Model (AppxManifest.xml),")
        print("       NOT via the shell\\open\\command registry value written above.")
        print("       The registry patch above has NO EFFECT on double-click behavior.")
        print()
        print("  How to make pyexewrap the default handler despite MSIX:")
        print("    Option A: Uninstall 'Python Manager' from the Microsoft Store.")
        print("              After uninstalling, the HKLM ftype layer (Layer 2) takes effect.")
        print("    Option B: Install Python from https://www.python.org/downloads/")
        print("              (classic installer, not Store) to get the traditional launcher.")
        print("    Option C: Windows Settings > Apps > Default apps > set .py/.pyw manually.")
    else:
        print("\n  No HKCU AppX handlers found (not using MSIX Python Manager).")

    # --- Layer 2: HKLM ftype (classic fallback, requires admin) ---
    if not is_admin():
        print("\n  [!] Skipping HKLM ftype update (requires admin).")
        print("      Re-run as admin or use --elevate to also update the classic ftype layer.")
    else:
        d = diagnose()
        prog_ids_done = set()
        print("\n  Updating HKLM ftype (classic layer):")
        for ext in d.extensions:
            pid = ext.prog_id_effective
            if not pid or pid in prog_ids_done:
                continue
            set_command(pid, command)
            print(f"    Set {pid} -> {command}")
            prog_ids_done.add(pid)

    print("\nDone. pyexewrap is now the default handler for .py and .pyw files.")
    print("Run 'py -m winpyfiles diagnose' to verify.")

    if _is_double_clicked():
        input("\nPress Enter to close...")


def _is_double_clicked():
    return len(sys.argv) == 1 and sys.stdin and sys.stdin.isatty()


if __name__ == "__main__":
    main()
