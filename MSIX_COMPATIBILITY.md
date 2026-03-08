# pyexewrap and the MSIX Python Manager — compatibility notes

## How pyexewrap is invoked (the normal chain)

pyexewrap relies on a specific chain of events when a user double-clicks a `.py` file:

```
Double-click on script.py
  → Windows Explorer resolves the file handler
  → launches py.exe "script.py"
  → py.exe reads the shebang: #!/usr/bin/env python -m pyexewrap
  → py.exe re-invokes: python.exe -m pyexewrap script.py
  → pyexewrap wraps and executes the script
```

Two components are essential:

1. **`py.exe`** (the Windows Python Launcher) must be the program that opens `.py` files.
   Only `py.exe` knows how to read shebang lines — `python.exe` itself ignores them entirely
   (the `#!` line is treated as a regular Python comment).

2. **pyexewrap must be importable** by the Python environment that `py.exe` selects.
   This is ensured by `add_to_pythonpath.py`, which adds the repo to the system PYTHONPATH.

## Full compatibility matrix (confirmed by testing)

| Invocation method | Works with MSIX? | Works without MSIX? |
|---|---|---|
| Shebang `#!/usr/bin/env python -m pyexewrap` | **Yes** ✓ | **Yes** ✓ |
| `register.py` → `pyexewrap.PyFile` ProgID | **Yes** ✓ | **Yes** ✓ |
| `activate.py` AppX HKCU layer | **No** ✗ | N/A |
| `activate.py` HKLM ftype layer (`--elevate`) | **No** ✗ | **Yes** ✓ |

## The MSIX Python Manager

The `PythonSoftwareFoundation.PythonManager` package (from the Microsoft Store or the
"Python Install Manager" on python.org) uses **Windows App Model activation** to handle
`.py`/`.pyw` double-clicks. This activation is declared in `appxmanifest.xml`:

```xml
<Application Id="Python.Exe" ...>
  <Extensions>
    <uap3:Extension Category="windows.fileTypeAssociation">
      <uap3:FileTypeAssociation Name="python-file">
        <uap:SupportedFileTypes>
          <uap:FileType>.py</uap:FileType>
          <uap:FileType>.pyw</uap:FileType>
        </uap:SupportedFileTypes>
      </uap3:FileTypeAssociation>
    </uap3:Extension>
  </Extensions>
</Application>
```

When this package is installed, Windows bypasses the registry ftype entirely and invokes the
MSIX application declared in the manifest — the pymanager launcher (`py.exe`). This launcher:

- **Reads shebang lines** → the shebang approach works correctly with MSIX.
- **For files without shebangs** → consults `HKCU\Software\Classes\.py\OpenWithProgids` and
  finds `pyexewrap.PyFile` if `register.py` was run → invokes pyexewrap via that ProgID.

### What is bypassed by MSIX

All changes to `shell\open\command` registry keys (made by `winpyfiles set-command`,
`activate.py`'s AppX layer, or `py -m winpyfiles reset`) have **no effect** on double-click
behavior while the MSIX package is installed. The App Model reads `appxmanifest.xml` directly.

### What is NOT bypassed

`HKCU\Software\Classes\pyexewrap.PyFile\shell\open\command` is a standard HKCU ProgID key,
not an AppX key. It is read by the pymanager launcher as part of its file handling logic, not
by the App Model itself. This is why `register.py`'s approach works under MSIX.

## How to switch ByDefaultActivation on and off

### Enable (all .py files wrapped, with or without shebang)

```
py tools/ByDefaultActivation/register.py          # required: registers pyexewrap.PyFile
py tools/ByDefaultActivation/activate.py           # optional: also patches AppX/HKLM layers
py tools/ByDefaultActivation/activate.py --elevate # with HKLM update (non-MSIX systems)
```

### Disable (back to plain Python on double-click)

```
py tools/ByDefaultActivation/reset.py              # removes AppX/HKLM overrides
py tools/ByDefaultActivation/reset.py --elevate    # with HKLM reset
```

> **Note:** `reset.py` does not remove the `pyexewrap.PyFile` ProgID from `register.py`.
> On MSIX systems, the pymanager launcher will continue to use pyexewrap for no-shebang scripts
> until that ProgID is removed manually (see `tools/ByDefaultActivation/README.md`).

### Diagnose current state

```
py tools/ByDefaultActivation/diagnose.py
# or equivalently:
py -m winpyfiles diagnose
```

## Long-term outlook

The Python 3.14 documentation officially deprecates the classic Python Launcher:

> *"Deprecated since Python 3.14, will not be produced for Python 3.16+"*

And the python.org downloads page states:

> *"The traditional installer will remain available throughout the 3.14 and 3.15 releases."*

This means:
- `C:\Windows\py.exe` (classic launcher) disappears with Python 3.16
- The classic Setup.exe (which configures the HKLM ftype registry) may also disappear

**Impact on pyexewrap:**
- **Shebang approach**: continues to work — the MSIX launcher reads shebangs.
- **ByDefaultActivation via `register.py`**: continues to work — the pymanager launcher reads
  the `pyexewrap.PyFile` HKCU ProgID.
- **ByDefaultActivation via `activate.py` HKLM layer**: stops working when the classic
  Setup.exe disappears, as there will be no `Python.File` HKLM ftype to patch.
