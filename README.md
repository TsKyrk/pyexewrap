# pyexewrap
A python script wrapping all the other python scripts under windows.
The aim is to stop the console from closing abruptly in situations where the user was expecting to have something read.
The "Press Enter to continue." message will only show up if the script is double-clicked.
The message will still appear if an exception occured before the end.

# Installation
The path to this package shall be added to your PYTHONPATH to be visible from any location.
You need to have administrator rights for this.
This can be done using the Windows GUI (*the recommended way*): see Desktop>Properties>... 
or a PowerShell command (not recommended unless you know what you are doing. *I dont... this is not tested.*):
```commandline
$PYTHONPATH = [Environment]::GetEnvironmentVariable("PYTHONPATH")
$pyexewrap_path = "C:\your\path\here\pyexewrap"
[Environment]::SetEnvironmentVariable("PYTHONPATH", "$PYTHONPATH;$pyexewrap_path")
```
or a cmd command (not recommended unless you know what you are doing. *I dont... this is not tested.*):
```commandline
setx /M PYTHONPATH "%PYTHONPATH%;C:\your\path\here\pyexewrap"
```

# Usage
Using shebang on the first line of your scripts (the main purpose of this tool):
```commandline
#!/usr/bin/env/ python -m pyexewrap
```
Your .py file extensions must be associated with the Windows Python Launcher (C:\Windows\py.exe) which comes with any Python installer downloaded from the official python website.
It appears that you may not have py.exe installed if your Python has been installed from the Windows Store.
Contrary to python.exe, py.exe has the ability to read shebang lines with "virtual commands".
More info here: https://python.readthedocs.io/en/latest/using/windows.html#shebang-lines

Using command line interface (CLI):
```commandline
python -m pyexewrap <myscript.py>
```

