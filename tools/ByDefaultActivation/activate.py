"""Activate pyexewrap as the default handler for .py and .pyw files.

Sets the shell open command for every effective Python ProgID so that
double-clicking a .py or .pyw file routes through pyexewrap.

Requires administrator rights (UAC prompt triggered automatically).
"""
import sys
import os

# Allow running directly from this folder without installing the packages.
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from winpyfiles import diagnose, find_py_exe, set_command
from winpyfiles._elevation import is_admin, elevate_and_rerun
from winpyfiles._backup import backup


def main():
    if not is_admin():
        elevate_and_rerun()
        return

    py_exe = find_py_exe()
    if not py_exe:
        print("[!] py.exe not found. Is the Python Launcher installed?")
        sys.exit(1)

    # Save current state before modifying anything.
    saved = backup()
    print(f"Backup saved: {saved}")

    command = (
        f'cmd /c set "pyexewrap_simulate_doubleclick=1"'
        f'&&"{py_exe}" -m pyexewrap "%1" %*'
    )

    d = diagnose()
    prog_ids_done = set()
    for ext in d.extensions:
        pid = ext.prog_id_effective
        if not pid:
            print(f"  [!] {ext.extension}: no effective ProgID -- skipped")
            continue
        if pid in prog_ids_done:
            continue
        set_command(pid, command)
        print(f"  Set {pid} -> {command}")
        prog_ids_done.add(pid)

    if not prog_ids_done:
        print("[!] No effective ProgIDs found. Nothing was changed.")
        sys.exit(1)

    print("\nDone. pyexewrap is now the default handler for .py and .pyw files.")
    print("Run 'py -m winpyfiles diagnose' to verify.")

    # Pause when double-clicked.
    if _is_double_clicked():
        input("\nPress Enter to close...")


def _is_double_clicked():
    """Heuristic: no arguments and running as a frozen exe or via Explorer."""
    return len(sys.argv) == 1 and sys.stdin and sys.stdin.isatty()


if __name__ == "__main__":
    main()
