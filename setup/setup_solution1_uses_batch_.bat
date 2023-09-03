@echo off
setlocal enabledelayedexpansion

:option
REM The /M option of setx adds the PYTHONPATH for all the users but this requires admin privileges.
REM If you don't have them your may comment the following line and run the script again.
REM Just use the REM prefix on the next line:
set "option=/M "

:get_current_PYTHONPATH
set "current_PYTHONPATH=%PYTHONPATH%"
echo Initial PYTHONPATH=%current_PYTHONPATH%
echo.

REM goto :get_parent_dir
:safety_block
if not "%current_PYTHONPATH%"=="" (
	echo The PYTHONPATH variable already exists in your system.
	echo Please copy its content in a safe place before using this script.
	echo Then edit this script to delete completely the :safety_block.
	echo Then cross your fingers and run the script again^^!
	echo.
	goto :end_script
)

:get_parent_dir
set "script_dir=%~dp0"
REM Remove trailing backslash if present
if "%script_dir:~-1%"=="\" (
    set "script_dir=!script_dir:~0,-1!"
)
for %%I in ("%script_dir%") do set "parent_dir=%%~dpI"

:cleanup_parent_dir
REM escape the last backslash in parent_dir
if "%parent_dir:~-1%"=="\" (
    set "parent_dir=%parent_dir%\"
)
echo parent_dir=%parent_dir%
echo.

:input
REM Ask the user if they want to add the path to PYTHONPATH
set /p add_to_PYTHONPATH=Do you want to add this path to PYTHONPATH? (Y/N):
if /i not "%add_to_PYTHONPATH%"=="Y" (
	echo Path not added to PYTHONPATH.
	goto :end_script
)

:check_if_already_exists
echo !current_PYTHONPATH! | findstr /C:"%parent_dir%" >nul
if not errorlevel 1 (
	echo Path already exists in PYTHONPATH. No changes made.
	goto :end_script
)

:building_new_PYTHONPATH
if "!current_PYTHONPATH!"=="" (
	REM If PYTHONPATH is empty, set it to the new path
	set "new_PYTHONPATH=%parent_dir%"
) else (
	REM If it doesn't exist, append it to PYTHONPATH
	set "new_PYTHONPATH=!current_PYTHONPATH!;%parent_dir%"
)

:adding_path_to_PYTHONPATH
setx %option%PYTHONPATH "!new_PYTHONPATH!"
if errorlevel 1 (
	echo Failed editing PYTHONPATH. You may need to run this script as an administrator.
	echo.
) else (
	echo Path added to PYTHONPATH.
	echo.
	echo Final PYTHONPATH=!new_PYTHONPATH!
	echo.
)

:end_script
pause
