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

## Why the MSIX Python Manager breaks this chain

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

When this package is installed, Windows bypasses the registry entirely for `.py` double-clicks
and invokes the application declared in the manifest — directly launching `python.exe` with the
clicked file as argument:

```
Double-click on script.py
  → Windows App Model reads appxmanifest.xml           ← bypasses registry
  → launches python.exe script.py directly             ← py.exe is skipped
  → python.exe sees #! as a comment, ignores shebang   ← pyexewrap is never called
  → script runs without pyexewrap
```

The consequence: **all registry changes made by `winpyfiles` (ftype, assoc, shell\open\command)
have no effect** as long as the MSIX package is installed. The App Model takes priority over the
entire registry ftype mechanism.

## Why `winpyfiles` cannot override this

`winpyfiles set-command` writes to `HKCU\Software\Classes\<ProgID>\shell\open\command`. This
works for classic (non-MSIX) file associations. For MSIX-registered file types, the App Model
activation reads `appxmanifest.xml` directly — it does not go through `shell\open\command` at
all. Even writing to the AppX ProgID keys in HKCU (`AppX...`) has no effect on what is actually
executed when the file is opened.

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

The python.org downloads page states:

> *"The traditional installer will remain available throughout the 3.14 and 3.15 releases."*

This suggests the classic Setup.exe (which installs `C:\Windows\py.exe` and uses the HKLM ftype
mechanism) may be removed in a future Python version. If Python moves entirely to MSIX
distribution, pyexewrap's shebang-based invocation will stop working.

A future-proof alternative would require pyexewrap to be packaged as a real `.exe` (e.g. via
PyInstaller) registered as a Windows file handler — replacing the shebang mechanism entirely with
a proper ftype association that `winpyfiles` can control.
