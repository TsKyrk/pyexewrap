# pyexewrap and the MSIX Python Manager — compatibility notes

## How pyexewrap is invoked (the normal chain)

pyexewrap relies on a specific chain of events when a user double-clicks a `.py` file:

```
Double-click on script.py
  → Windows Explorer reads the registry ftype
  → launches C:\Windows\py.exe "script.py"
  → py.exe reads the shebang: #!/usr/bin/env python -m pyexewrap
  → py.exe re-invokes: python.exe -m pyexewrap script.py
  → pyexewrap wraps and executes the script
```

Two components are essential:

1. **`py.exe`** (the Windows Python Launcher) must be the program that opens `.py` files.
   Only `py.exe` knows how to read shebang lines — `python.exe` itself ignores them entirely
   (the `#!` line is treated as a regular Python comment).

2. **The Windows registry ftype** must point `.py` → `py.exe`.
   This is what `winpyfiles` inspects and configures.

## The MSIX Python Manager and shebangs

The `PythonSoftwareFoundation.PythonManager` package (available from the Microsoft Store and
from the "Python Install Manager" on python.org) uses **Windows App Model activation** to handle
`.py` and `.pyw` double-clicks. This activation mechanism is declared in `appxmanifest.xml`:

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

When this package is installed, Windows bypasses the registry entirely for `.py` double-clicks.
The App Model takes priority over the entire registry ftype mechanism — meaning all changes made
by `winpyfiles` (ftype, assoc, shell\open\command) have **no effect** on double-click behavior.

**However**, according to the [Python 3.14 documentation](https://docs.python.org/3.14/using/windows.html),
the MSIX Install Manager **does** include its own launcher that reads shebang lines:

> *"Both the modern Install Manager and deprecated launcher support Unix-style shebang lines."*

This means the chain with MSIX is likely:

```
Double-click on script.py
  → Windows App Model reads appxmanifest.xml           ← bypasses registry ftype
  → launches MSIX py.exe "script.py"                   ← MSIX launcher, not C:\Windows\py.exe
  → py.exe reads the shebang: #!/usr/bin/env python -m pyexewrap
  → py.exe invokes: python.exe -m pyexewrap script.py
  → python.exe searches for pyexewrap in its environment ← possible failure point
```

The shebang itself is probably read correctly. The likely failure point is that
**`python -m pyexewrap` fails because pyexewrap is not visible in the MSIX Python environment**.
The MSIX Python may have partial isolation from the system `PYTHONPATH`, meaning the
`add_to_pythonpath.py` installation step has no effect on it.

This hypothesis has not been confirmed by testing — further investigation is needed.

## Why `winpyfiles` cannot override the file association

`winpyfiles set-command` writes to `HKCU\Software\Classes\<ProgID>\shell\open\command`. This
works for classic (non-MSIX) file associations. For MSIX-registered file types, the App Model
activation reads `appxmanifest.xml` directly — it does not go through `shell\open\command` at
all. Even writing to the AppX ProgID keys in HKCU (`AppX...`) has no effect on what application
is activated when the file is opened.

## Detection and resolution

**Detect** with `py -m winpyfiles diagnose`. If the MSIX package is installed, the output shows:

```
[!!] MSIX Python Manager detected -- AppX handlers found in HKCU\Software\Classes
```

**Resolve** with `py -m winpyfiles remove-msix`, which runs:

```powershell
Get-AppxPackage -Name 'PythonSoftwareFoundation.PythonManager' | Remove-AppxPackage
```

After removal, the classic registry ftype mechanism is restored and `winpyfiles` can configure
it normally.

> **Important:** After removing the MSIX package, you must install a Python runtime separately.
> The MSIX provided both the launcher and the runtime. Install the classic Setup.exe from
> https://www.python.org/downloads/windows/ (the file named `python-3.x.x-amd64.exe`,
> listed under "Windows installer (64-bit)") to restore `C:\Windows\py.exe` and the HKLM ftype.

## Long-term outlook

The Python 3.14 documentation officially deprecates the classic Python Launcher:

> *"Deprecated since Python 3.14, will not be produced for Python 3.16+"*

And the python.org downloads page states:

> *"The traditional installer will remain available throughout the 3.14 and 3.15 releases."*

This means:
- `C:\Windows\py.exe` (classic launcher) disappears with Python 3.16
- The classic Setup.exe (which configures the HKLM ftype registry) may also disappear
- pyexewrap's shebang-based invocation becomes unsupported from Python 3.16 onward

### Possible paths forward

**Option 1 — Adapt to the MSIX Install Manager**
If the failure is only a `PYTHONPATH` visibility issue (and not a fundamental bypass of shebang
processing), pyexewrap might work with the MSIX Install Manager once its module is accessible to
the MSIX Python environment. This requires investigation and possibly a different installation
strategy (e.g. `pip install` into the MSIX Python, or a `pymanager.json` config hook).

The MSIX Install Manager also has a `shebang_can_run_anything` configuration option that may
need to be enabled for the `python -m pyexewrap` shebang to be accepted.

**Option 2 — Package pyexewrap as a real `.exe`**
Build a `pyexewrap.exe` (e.g. via PyInstaller) and register it as a Windows file handler via
`winpyfiles`. This replaces the shebang mechanism entirely with a proper ftype association,
making pyexewrap independent of `py.exe` and compatible with any Python distribution.
This is a significant refactor but the most future-proof approach.

**Option 3 — ByDefaultActivation with a batch wrapper**
The existing `tools/ByDefaultActivation` approach (associating `.py` with a batch file that
calls pyexewrap) already bypasses the need for shebangs. However it still depends on the
registry ftype mechanism being in effect, which MSIX overrides.
