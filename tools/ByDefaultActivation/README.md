# ByDefaultActivation tool

This tool lets you activate pyexewrap **globally** for all `.py` and `.pyw` files on your machine, without needing to add a shebang line to each script.

It works by changing the Windows file-type association (`ftype`) for `Python.File` and `Python.NoConFile` so that double-clicking any Python script automatically goes through pyexewrap.

> **Warning:** These scripts modify system-level settings (`assoc` / `ftype`).
> You need administrator rights to run them.
> No backup of the previous settings is made — run script `01` first to note the current state.

---

## Scripts

### `01_check_current_system_settings.bat`
Displays the current `assoc` and `ftype` entries for Python files (`.py`, `.pyw`).
Run this **before** making any change to note the original state of your system.

### `02_Set__ByDefaultActivation.bat`
Activates pyexewrap as the default handler for `.py` and `.pyw` files.

Sets the following `ftype` commands:
```
Python.File    → cmd /c set "pyexewrap_simulate_doubleclick=1" && py.exe -m pyexewrap "%L" %*
Python.NoConFile → cmd /c set "pyexewrap_simulate_doubleclick=1" && py.exe -m pyexewrap "%L" %*
```

Requires write access to the registry. If it fails silently, use the `AsAdmin` variant below.

### `02_Set__ByDefaultActivation_AsAdmin.bat`
Same as `02_Set__ByDefaultActivation.bat` but triggers a UAC elevation prompt to run with administrator rights.

### `03_Reset__Pyexe.bat`
Reverts the file-type associations back to the standard `py.exe` handler:
```
Python.File    → py.exe "%L" %*
Python.NoConFile → py.exe "%L" %*
```

### `03_Reset__Pyexe_AsAdmin.bat`
Same as `03_Reset__Pyexe.bat` but triggers a UAC elevation prompt to run with administrator rights.

---

## Registry Files

For direct registry manipulation (alternative to the batch scripts above), you can use these `.reg` files:

### `04_Reset__Open_Python.File_with_c_windows_pyexe.reg`
Resets the file association back to the standard `py.exe` handler by directly modifying the registry.

### `05_Activation__Open_Python.File_with_pyexewrap.reg`
Activates pyexewrap as the default handler by directly modifying the registry.

### `06_Activate_Default.reg`
Hex-encoded version that activates pyexewrap with double-click simulation.

### `07_OpenWithIDLE.reg`
Adds an "Edit with IDLE" option to the context menu for Python files.

### `08_Open_Python.File_with_py.exe_executable.reg`
Hex-encoded version that sets the default handler to `py.exe`.

> **Note:** Registry files require administrator rights and modify system settings directly. Use with caution.

---

## Typical workflow

1. Run `01_check_current_system_settings.bat` and note your current settings.
2. Run `02_Set__ByDefaultActivation_AsAdmin.bat` to activate pyexewrap globally.
3. Double-click any `.py` or `.pyw` file — it will now run through pyexewrap.
4. To revert, run `03_Reset__Pyexe_AsAdmin.bat`.
