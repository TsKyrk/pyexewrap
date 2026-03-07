"""CLI entry point: python -m winpyfiles [command]"""
import sys

from ._assoc import diagnose, find_py_exe, find_msix_python_package, set_command
from ._backup import backup, restore
from ._elevation import is_admin, elevate_and_rerun


def _interpret_command(command):
    """Return a human-readable status for a ftype command string."""
    if not command:
        return "[!] NOT CONFIGURED -- double-clicking this file type will likely fail"
    if "py.exe" in command.lower() or "python" in command.lower():
        return "[OK] Python launcher configured"
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

Windows reads settings from registry locations, in priority order:
  UserChoice  (HKCU\\...\\Explorer\\FileExts\\<ext>\\UserChoice)
              -- Windows 8+ Explorer override, highest priority for double-clicks
              -- Set by the user via "Open with > Always use this app"
              -- Cannot be changed programmatically (protected by a hash)
  HKCU  (HKEY_CURRENT_USER)  -- your personal settings
  HKLM  (HKEY_LOCAL_MACHINE) -- system-wide settings, fallback
  Active = the value actually used when UserChoice is absent
""")

    print("--- Step 1: Extension -> ProgID ---\n")
    for ext in d.extensions:
        active = ext.prog_id_effective or "(not set)"
        uc = ext.user_choice
        print(f"  {ext.extension}")
        print(f"    UserChoice      : {uc or '(not set)'}", end="")
        if uc:
            print("  <-- Explorer uses this for double-clicks (overrides HKCU/HKLM)")
        else:
            print("  <-- not set, Explorer falls back to Active below")
        print(f"    HKCU   (user)   : {ext.prog_id_hkcu or '(not set)'}")
        print(f"    HKLM   (system) : {ext.prog_id_hklm or '(not set)'}")
        print(f"    Active          : {active}")
        if not ext.prog_id_effective and not uc:
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

    print("--- MSIX AppX Handlers (Windows 10/11) ---\n")
    if d.msix_package:
        print(f"  Package detected : {d.msix_package}")
    if d.msix_handlers:
        print("  [!!] MSIX Python Manager detected -- AppX handlers found in HKCU\\Software\\Classes:")
        for prog_id, cmd in d.msix_handlers.items():
            print(f"    {prog_id}")
            print(f"      command : {cmd}")
        print()
        print("  [!!] CRITICAL: These AppX handlers are activated by the MSIX App Model, NOT by")
        print("       the shell\\open\\command registry value. Windows reads the handler's")
        print("       AppxManifest.xml directly and runs the bundled Python executable --")
        print("       completely bypassing ftype, assoc, and shell\\open\\command registry changes.")
        print()
        print("       This means: editing the registry (including HKCU AppX overrides) has NO")
        print("       EFFECT on what runs when you double-click a .py file on this machine.")
        print()
        print("  How to resolve:")
        print("    Option A: Uninstall 'Python Manager' (or 'Python Launcher') from the")
        print("              Microsoft Store. After uninstalling, the classic ftype registry")
        print("              mechanism takes over and can be configured normally.")
        print("    Option B: Install Python from https://www.python.org/downloads/ -- the")
        print("              classic installer places a real py.exe in C:\\Windows\\ and uses")
        print("              the traditional HKLM ftype mechanism instead of MSIX.")
        print("    Option C: In Windows Settings > Apps > Default apps, manually set the")
        print("              default app for .py/.pyw files to the desired Python launcher.")
    elif d.msix_package:
        print("  [!] Package found on disk but no AppX ProgIDs detected in registry.")
        print("      The MSIX block may still be active -- run diagnose after a fresh login.")
    else:
        print("  No MSIX Python Manager detected -- classic ftype registry mechanism is active.")
    print()

    print("--- Summary ---\n")
    warnings = []
    for ext in d.extensions:
        # For Explorer double-clicks: UserChoice wins if set.
        effective_pid = ext.user_choice or ext.prog_id_effective
        uc_marker = " (UserChoice)" if ext.user_choice else ""
        if not effective_pid:
            warnings.append(f"{ext.extension}: no ProgID -- extension is unmapped")
            continue
        info = d.prog_ids.get(effective_pid)
        cmd = info.command_effective if info else None
        status = _interpret_command(cmd)
        print(f"  {ext.extension}  ->  {effective_pid}{uc_marker}  ->  {status}")
        if ext.user_choice and ext.user_choice != ext.prog_id_effective:
            warnings.append(
                f"{ext.extension}: UserChoice '{ext.user_choice}' overrides registry ProgID "
                f"'{ext.prog_id_effective}' -- ftype/assoc changes have no effect for Explorer double-clicks"
            )
        if not cmd:
            warnings.append(f"{ext.extension}: ProgID '{effective_pid}' has no command")

    if d.msix_handlers:
        warnings.insert(0,
            "MSIX Python Manager is active -- registry ftype changes have NO EFFECT on "
            "double-clicks. See 'MSIX AppX Handlers' section above for how to resolve."
        )

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


def cmd_reset() -> None:
    """Reset all effective Python extension ProgIDs to use py.exe directly."""
    elevate = "--elevate" in sys.argv

    if not is_admin():
        if elevate:
            elevate_and_rerun()
        else:
            print("[!] Reset requires administrator rights.")
            print("    Add --elevate to trigger a UAC prompt automatically.")
            sys.exit(1)

    py_exe = find_py_exe()
    if not py_exe:
        print("[!] py.exe not found. Is the Python Launcher installed?")
        sys.exit(1)

    command = f'"{py_exe}" "%1" %*'
    d = diagnose()
    prog_ids_set = set()
    for ext in d.extensions:
        pid = ext.prog_id_effective
        if pid and pid not in prog_ids_set:
            set_command(pid, command)
            print(f"  Set {pid} -> {command}")
            prog_ids_set.add(pid)

    if not prog_ids_set:
        print("[!] No effective ProgIDs found. Nothing to reset.")
    else:
        print("Done. Run 'py -m winpyfiles diagnose' to verify.")


def cmd_set_command() -> None:
    """Set the open command for a given ProgID."""
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    elevate = "--elevate" in sys.argv

    if len(args) < 2:
        print("Usage: py -m winpyfiles set-command <ProgID> <command> [--elevate]")
        print("Example: py -m winpyfiles set-command Python.File '\"C:\\Windows\\py.exe\" \"%1\" %*'")
        sys.exit(1)

    prog_id, command = args[0], args[1]

    if not is_admin():
        if elevate:
            elevate_and_rerun()
        else:
            print("[!] set-command requires administrator rights.")
            print("    Add --elevate to trigger a UAC prompt automatically.")
            sys.exit(1)

    set_command(prog_id, command)
    print(f"Set {prog_id} -> {command}")
    print("Run 'py -m winpyfiles diagnose' to verify.")


COMMANDS = {
    "diagnose": cmd_diagnose,
    "backup": cmd_backup,
    "restore": cmd_restore,
    "reset": cmd_reset,
    "set-command": cmd_set_command,
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
