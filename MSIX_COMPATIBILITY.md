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

## The MSIX Python Manager: partial compatibility

The `PythonSoftwareFoundation.PythonManager` package (available from the Microsoft Store and
from the "Python Install Manager" on python.org) uses **Windows App Model activation** to handle
`.py` and `.pyw` double-clicks. This activation mechanism is declared in `appxmanifest.xml` and
**bypasses all registry ftype/assoc/shell\open\command settings**.

However, **the MSIX package includes its own `py.exe` launcher that reads shebang lines**.
According to the Python 3.14 documentation:

> *"Both the modern Install Manager and deprecated launcher support Unix-style shebang lines."*

### What works with MSIX

**Confirmed by testing (double-click on a `.py` file with the shebang):**

```
Double-click on script.py (MSIX installed)
  → Windows App Model reads appxmanifest.xml       ← bypasses registry ftype
  → launches MSIX py.exe "script.py"               ← MSIX py, not C:\Windows\py.exe
  → MSIX py.exe reads the shebang                  ← shebang IS processed
  → invokes: python.exe -m pyexewrap script.py
  → pyexewrap runs correctly                        ← confirmed working ✓
```

The shebang approach (`#!/usr/bin/env python -m pyexewrap`) **works correctly** with the
MSIX Python Manager, provided pyexewrap is in the PYTHONPATH (which the MSIX Python inherits
from the system environment).

### What does NOT work with MSIX

The **ByDefaultActivation** approach (the `tools/ByDefaultActivation/` scripts that modify the
registry `shell\open\command` to associate all `.py` files with pyexewrap without a shebang) is
**blocked by the MSIX App Model**. Any registry changes made by `winpyfiles set-command` or
`activate.py` have no effect on double-click behavior as long as the MSIX package is installed.

```
Double-click on script.py (no shebang, ByDefaultActivation configured)
  → Windows App Model reads appxmanifest.xml       ← bypasses registry ftype
  → launches MSIX python.exe "script.py" directly  ← pyexewrap bypassed ✗
  → script runs without pyexewrap
```

## Summary

| Invocation method | Works with MSIX? |
|---|---|
| Shebang `#!/usr/bin/env python -m pyexewrap` | **Yes** ✓ |
| ByDefaultActivation (registry ftype change) | **No** ✗ |
| CLI `py -m pyexewrap script.py` | **Yes** ✓ |
| Shortcut / batch wrapper | **Yes** ✓ |

## What `winpyfiles diagnose` warns about

`py -m winpyfiles diagnose` shows a `[!!] MSIX Python Manager detected` warning when the
package is installed. This warning targets **registry-based invocation** (ByDefaultActivation),
which is genuinely blocked by MSIX. It does not mean pyexewrap is broken — it means that
configuring `.py` file associations via the registry has no effect.

## Long-term outlook

The Python 3.14 documentation officially deprecates the classic Python Launcher:

> *"Deprecated since Python 3.14, will not be produced for Python 3.16+"*

And the python.org downloads page states:

> *"The traditional installer will remain available throughout the 3.14 and 3.15 releases."*

This affects the **classic `C:\Windows\py.exe`** (installed by the Setup.exe) which will
disappear with Python 3.16. The **MSIX py.exe** (from the Install Manager) is the replacement
and does support shebangs — so the primary pyexewrap use case (shebang-based invocation)
should remain functional.

The main concern is for users who relied on ByDefaultActivation (registry ftype) to run
pyexewrap on scripts without a shebang line. That path has no compatible replacement yet.
