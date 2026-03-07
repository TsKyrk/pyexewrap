# ByDefaultActivation

Activate or reset pyexewrap as the default handler for `.py` and `.pyw` files
on your machine — no shebang line needed in each script.

Works by writing the Windows file-type association for every effective Python
ProgID (`Python.File`, `Python.NoConsole`, …) via the registry.

> **Note:** Both scripts require administrator rights.
> A backup of the current associations is saved automatically before any change.

---

## Scripts

### `activate.py`
Activates pyexewrap as the default handler for `.py` and `.pyw` files.

- Triggers a UAC elevation prompt if not already admin.
- Backs up the current registry state to a `winpyfiles_backup_*.json` file.
- Sets the open command for every effective Python ProgID to:
  ```
  cmd /c set "pyexewrap_simulate_doubleclick=1" && py.exe -m pyexewrap "%1" %*
  ```

Run with:
```
py activate.py
```
Or double-click it — a UAC prompt will appear.

### `reset.py`
Resets `.py` and `.pyw` file associations back to the plain `py.exe` launcher.

- Triggers a UAC elevation prompt if not already admin.
- Backs up the current registry state before resetting.
- Sets the open command for every effective Python ProgID to:
  ```
  py.exe "%1" %*
  ```

Run with:
```
py reset.py
```
Or double-click it — a UAC prompt will appear.

---

## Typical workflow

1. Run `py -m winpyfiles diagnose` to see the current state.
2. Run `activate.py` to route all `.py`/`.pyw` double-clicks through pyexewrap.
3. Run `reset.py` to revert to the standard py.exe launcher.
4. To restore a specific saved state: `py -m winpyfiles restore <backup_file.json>`

---

## Deprecated

The previous batch scripts (`.bat`) and registry files (`.reg`) are kept in
[`deprecated/`](deprecated/) for reference only. They are superseded by the
Python scripts above, which use `winpyfiles` and auto-backup before any change.
