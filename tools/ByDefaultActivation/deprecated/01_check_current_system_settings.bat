@echo off

echo =========assoc==========
assoc | findstr -i py
echo.

echo =========ftype==========
ftype | findstr -i py
echo.

:pause
REM pause only if double-clicked:
echo %cmdcmdline%|find /i """%~f0""">nul && pause