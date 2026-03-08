# ByDefaultActivation

Make pyexewrap the default handler for **all** `.py` and `.pyw` files on double-click —
including scripts with no shebang line.

Without ByDefaultActivation, pyexewrap is only invoked for scripts that explicitly include:
```
#!/usr/bin/env python -m pyexewrap
```

## Quick reference

| Goal | Command |
|---|---|
| Enable (all .py files wrapped) | `py register.py` then `py activate.py` |
| Disable (back to plain Python) | `py reset.py` |
| Undo `register.py` completely | `py unregister.py` |
| Diagnose current state | `py diagnose.py` or `py -m winpyfiles diagnose` |
| Restore a saved state | `py -m winpyfiles restore <backup_file.json>` |

---

## How to enable

### Step 1 — `register.py` (no admin required)

```
py tools/ByDefaultActivation/register.py
```

Registers `pyexewrap` as a known application in Windows by creating a `pyexewrap.PyFile` ProgID
in `HKCU\Software\Classes`. This ProgID points to `python.exe -m pyexewrap "%1" %*`.

**This step is required for compatibility with the MSIX Python Manager.** The pymanager launcher
reads this HKCU ProgID for `.py` files that have no shebang line, and invokes pyexewrap
accordingly — even when the MSIX App Model bypasses the classic registry ftype mechanism.

### Step 2 — `activate.py` (admin optional)

```
py tools/ByDefaultActivation/activate.py
py tools/ByDefaultActivation/activate.py --elevate   # also update HKLM (classic systems)
```

Patches two registry layers:

1. **HKCU AppX handlers** (no admin) — writes pyexewrap to the `AppXxxxx\shell\open\command`
   keys registered by the MSIX Python Manager.

   > **Note:** These AppX keys are bypassed by the MSIX App Model, which reads
   > `appxmanifest.xml` directly. Use `register.py` (Step 1) for MSIX compatibility.

2. **HKLM ftype** (admin required, `--elevate`) — sets `Python.File\shell\open\command` to
   `py.exe -m pyexewrap "%1" %*` for systems using the classic registry ftype mechanism
   (non-MSIX Python installations).

A backup of the current registry state is saved automatically before any change.

---

## How to disable

### `reset.py` (admin optional)

```
py tools/ByDefaultActivation/reset.py
py tools/ByDefaultActivation/reset.py --elevate   # also reset HKLM
```

Removes the AppX HKCU overrides written by `activate.py` and resets the HKLM ftype back to
plain `py.exe "%1" %*`. Backs up the current state before any change.

> **Note:** `reset.py` does **not** remove the `pyexewrap.PyFile` ProgID created by `register.py`.
> Scripts without a shebang will still be wrapped by pyexewrap on MSIX systems after `reset.py`.
>
> To fully undo `register.py`, run:
> ```
> py tools/ByDefaultActivation/unregister.py
> ```

---

## Compatibility with the MSIX Python Manager

The MSIX Python Manager (`PythonSoftwareFoundation.PythonManager`) uses Windows App Model
activation for `.py`/`.pyw` double-clicks, which bypasses all `ftype`/`shell\open\command`
registry changes. Despite this, ByDefaultActivation works via `register.py`:

| Script | Works with MSIX? | Mechanism |
|---|---|---|
| `register.py` | **Yes** ✓ | HKCU `pyexewrap.PyFile` ProgID (read by pymanager launcher) |
| `activate.py` AppX layer | **No** ✗ | AppX `shell\open\command` (bypassed by App Model) |
| `activate.py` HKLM layer | **Yes, without MSIX** | Classic registry ftype |

See [MSIX_COMPATIBILITY.md](../../MSIX_COMPATIBILITY.md) for the full compatibility matrix.

---

## Deprecated

The previous batch scripts (`.bat`) and registry files (`.reg`) are kept in
[`deprecated/`](deprecated/) for reference only. They are superseded by the
Python scripts above, which use `winpyfiles` and auto-backup before any change.
