# ByDefaultActivation

Make pyexewrap the default handler for **all** `.py` and `.pyw` files on double-click —
including scripts with no shebang line.

Without ByDefaultActivation, pyexewrap is only invoked for scripts that explicitly include:
```
#!/usr/bin/env python -m pyexewrap
```

## Quick reference

| Goal | How |
|---|---|
| Enable (all .py files wrapped) | Double-click `activate.bat`, or run `py activate.py` from CLI |
| Disable (back to plain Python) | Double-click `disable.bat`, or run `py disable.py` from CLI |
| Diagnose current state | `py diagnose.py` or `py -m winpyfiles diagnose` |
| Restore a saved state | `py -m winpyfiles restore <backup_file.json>` |

---

## How to enable

```
py tools/ByDefaultActivation/activate.py
```

Automatically detects the Python installation type and applies the right configuration:

- **MSIX Python Manager** (Microsoft Store / Python Install Manager): registers the
  `pyexewrap.PyFile` ProgID, then prompts you to set pyexewrap as the default via Windows
  Settings. This manual step is required because the MSIX App Model bypasses all registry
  ftype changes — only UserChoice (set via the UI) takes effect.

- **Classic Python** (no MSIX, `python-x.x.x-amd64.exe` installer): registers the ProgID
  and updates the HKLM ftype registry. A UAC prompt appears automatically if admin rights
  are needed. pyexewrap becomes the default immediately, no UI interaction required.

A backup of the current registry state is saved automatically before any change.

---

## How to disable

```
py tools/ByDefaultActivation/disable.py
```

Automatically detects the Python installation type and undoes the corresponding configuration:

- **MSIX Python Manager**: removes the `pyexewrap.PyFile` ProgID. Windows typically clears
  the UserChoice automatically when the ProgID disappears. If needed, the script shows
  instructions to clear it manually.

- **Classic Python**: removes the ProgID and resets the HKLM ftype to the plain Python
  launcher. A UAC prompt appears automatically if admin rights are needed.

A backup of the current registry state is saved automatically before any change.

---

## Compatibility with the MSIX Python Manager

The MSIX Python Manager (`PythonSoftwareFoundation.PythonManager`) uses Windows App Model
activation for `.py`/`.pyw` double-clicks, which bypasses all `ftype`/`shell\open\command`
registry changes. ByDefaultActivation works via UserChoice:

| Method | Works with MSIX? | Mechanism |
|---|---|---|
| `activate.py` (MSIX path) | **Yes** ✓ | `pyexewrap.PyFile` ProgID + UserChoice set via UI |
| `activate.py` (classic path) | **Yes, without MSIX** | HKLM ftype registry |

See [MSIX_COMPATIBILITY.md](../../MSIX_COMPATIBILITY.md) for the full compatibility matrix.

---

## Deprecated

The previous batch scripts (`.bat`) and registry files (`.reg`) are kept in
[`deprecated/`](deprecated/) for reference only.
