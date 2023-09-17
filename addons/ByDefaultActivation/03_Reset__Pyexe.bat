@echo off

ftype Python.File=C:\Windows\py.exe "%%L" %%*
ftype Python.NoConFile=C:\Windows\py.exe "%%L" %%*

assoc .py=Python.File
assoc .pyw=Python.NoConsole

:pause
REM pause only if double-clicked:
echo %cmdcmdline%|find /i """%~f0""">nul && pause