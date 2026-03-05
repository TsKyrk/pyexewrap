@echo off

ftype Python.File=cmd /c set "pyexewrap_simulate_doubleclick=1"^&^&C:\Windows\py.exe -m pyexewrap "%%L" %%*
ftype Python.NoConFile=cmd /c set "pyexewrap_simulate_doubleclick=1"^&^&C:\Windows\py.exe -m pyexewrap "%%L" %%*

assoc .py=Python.File
assoc .pyw=Python.NoConsole

:pause
REM pause only if double-clicked:
echo %cmdcmdline%|find /i """%~f0""">nul && pause