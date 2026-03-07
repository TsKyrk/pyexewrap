"""CLI entry point: python -m winpyfiles [command]"""
import sys

from ._assoc import diagnose
from ._backup import backup, restore
from ._elevation import is_admin, elevate_and_rerun


def _interpret_command(command):
    """Return a human-readable status for a ftype command string."""
    if not command:
        return "[!] NOT CONFIGURED -- double-clicking this file type will likely fail"
    if "pyexewrap" in command.lower():
        return "[OK] pyexewrap active"
    if "py.exe" in command.lower() or "python" in command.lower():
        return "[-] standard Python launcher (no pyexewrap)"
    return "[?] unknown handler"


def cmd_diagnose() -> None:
    d = diagnose()

    print("=" * 60)
    print("  Windows Python File Association Diagnosis")
    print("=" * 60)
    print("""
How Windows resolves file associations
---------------------------------------
When you double-click a .py or .pyw file, Windows looks up
which program should open it. This is done in two steps:

  1. Extension -> ProgID
     Each extension (.py, .pyw) points to a "ProgID", which is
     a named file type (e.g. "Python.File").

  2. ProgID -> Command
     The ProgID defines the command line that Windows executes.

Windows reads settings from two registry locations:
  HKCU  (HKEY_CURRENT_USER)  -- your personal settings, priority
  HKLM  (HKEY_LOCAL_MACHINE) -- system-wide settings, fallback
  Active = the value actually used (HKCU overrides HKLM if set)
""")

    print("--- Step 1: Extension -> ProgID ---\n")
    for ext in d.extensions:
        active = ext.prog_id_effective or "(not set)"
        print(f"  {ext.extension}")
        print(f"    HKCU   (user)   : {ext.prog_id_hkcu or '(not set)'}")
        print(f"    HKLM   (system) : {ext.prog_id_hklm or '(not set)'}")
        print(f"    Active          : {active}")
        if not ext.prog_id_effective:
            print(f"    [!] No ProgID found -- this extension has no handler!")
        print()

    print("--- Step 2: ProgID -> Command ---\n")
    for prog_id, info in d.prog_ids.items():
        status = _interpret_command(info.command_effective)
        print(f"  ProgID: {prog_id}")
        print(f"    HKCU   (user)   : {info.command_hkcu or '(not set)'}")
        print(f"    HKLM   (system) : {info.command_hklm or '(not set)'}")
        print(f"    Active          : {info.command_effective or '(not set)'}")
        print(f"    Status          : {status}")
        print()

    print("--- Summary ---\n")
    warnings = []
    for ext in d.extensions:
        prog_id = ext.prog_id_effective
        if not prog_id:
            warnings.append(f"{ext.extension}: no ProgID -- extension is unmapped")
            continue
        info = d.prog_ids.get(prog_id)
        cmd = info.command_effective if info else None
        status = _interpret_command(cmd)
        print(f"  {ext.extension}  ->  {prog_id}  ->  {status}")
        if not cmd:
            warnings.append(f"{ext.extension}: ProgID '{prog_id}' has no command")

    if warnings:
        print("\n  Warnings:")
        for w in warnings:
            print(f"    [!] {w}")
    print()


def cmd_backup() -> None:
    path = sys.argv[2] if len(sys.argv) > 2 else None
    saved = backup(path)
    print(f"Backup saved: {saved}")


def cmd_restore() -> None:
    if len(sys.argv) < 3:
        print("Usage: py -m winpyfiles restore <backup_file.json>")
        sys.exit(1)
    path = sys.argv[2]
    elevate = "--elevate" in sys.argv

    if not is_admin():
        if elevate:
            elevate_and_rerun()
        else:
            print("[!] Restore requires administrator rights.")
            print("    Add --elevate to trigger a UAC prompt automatically.")
            sys.exit(1)

    restore(path)
    print(f"Restored from: {path}")
    print("Run 'py -m winpyfiles diagnose' to verify.")


COMMANDS = {
    "diagnose": cmd_diagnose,
    "backup": cmd_backup,
    "restore": cmd_restore,
}


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "diagnose"
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Available commands: {', '.join(COMMANDS)}")
        sys.exit(1)
    COMMANDS[cmd]()


if __name__ == "__main__":
    main()
