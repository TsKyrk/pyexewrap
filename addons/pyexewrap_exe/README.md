# pyexewrap_exe add-on

This add-on packages pyexewrap as a standalone `pyexewrap.exe` executable using PyInstaller, then registers it as the default handler for `.py` files.

This is an alternative to the `ByDefaultActivation` add-on: instead of calling `py.exe -m pyexewrap` on each launch, the association points directly to a self-contained executable — no Python installation is required to trigger the wrapper.

> **Warning:** Scripts `02_setup.bat` and `03_revert.bat` modify system-level file-type associations and require administrator rights.
> `02_setup.bat` saves a backup of the current settings in `Backup_Full.txt` and `Backup_One.txt` before making changes.

---

## Scripts

### `pyexewrap_exe.py`
Thin Python wrapper used as the PyInstaller entry point.
Calls `py -m pyexewrap <script> [args...]` via `subprocess`, forwarding all arguments.
This file is compiled into `pyexewrap.exe` by `01_make_exe.bat`.

### `01_make_exe.bat`
Builds `pyexewrap.exe` from `pyexewrap_exe.py` using PyInstaller (`--onefile`),
then copies the resulting executable into the Python `Scripts/` folder so it is available on the system `PATH`.

Steps performed:
1. `pip install pyinstaller`
2. `pyinstaller --onefile pyexewrap_exe.py --name pyexewrap`
3. Copies `dist/pyexewrap.exe` → `<python>/Scripts/pyexewrap.exe`

### `02_setup.bat`
Registers `pyexewrap.exe` as the handler for `Python.File` (i.e. `.py` files) with a UAC elevation prompt.

Steps performed:
1. Checks whether the association is already set (cancels if so)
2. Backs up the current `ftype` settings to `Backup_Full.txt` and `Backup_One.txt`
3. Sets: `ftype Python.File="<Scripts>/pyexewrap.exe" "%L" %*`

### `03_revert.bat`
Restores the original `Python.File` association from the backup saved by `02_setup.bat` (`Backup_One.txt`), with a UAC elevation prompt.

---

## Typical workflow

1. Run `01_make_exe.bat` to build and install `pyexewrap.exe`.
2. Run `02_setup.bat` to register it as the default handler for `.py` files.
3. Double-click any `.py` file — it will now run through pyexewrap.
4. To revert, run `03_revert.bat`.

## Difference from ByDefaultActivation

| | ByDefaultActivation | pyexewrap_exe |
|---|---|---|
| Requires Python at launch | Yes (`py.exe`) | No (standalone `.exe`) |
| Backup of original settings | No | Yes (`Backup_*.txt`) |
| Build step needed | No | Yes (PyInstaller) |
