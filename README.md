# What is pyexewrap ?
When a .py file is double-clicked in the Windows file explorer, the script will pop a console that will most likely flash at the user's screen unless the last line of code has some blocking command like 
```commandline
input("Press ENTER to continue")
```
Yet if an exception occurs, which is common in development phase, the console will flash anyway.
Moreover, if the same script is run from the command line interface or is called by another script, the blocking line becomes undesirable.

Pyexewrap is a python script that, once setup on the OS, will wrap all the other python scripts enhanced with the proper shebang line.
On the enhanced scripts, the pausing message "Press Enter to continue." will show up only if the script is directly double-clicked, not when it is called or launched through CLI.
The pausing message will still appear if an exception occurs before the end.

# Installation
The path to this package shall be added to your PYTHONPATH environment variable to be visible from any location.
You need to have administrator rights for this.
This can be done using the Windows GUI (**the recommended way**): 

see Desktop>Properties>Advanced settings>Environment variables... 

or a PowerShell command (not recommended unless you know what you are doing. **I don't recommend this since I did not test it!**:
```commandline
$PYTHONPATH = [Environment]::GetEnvironmentVariable("PYTHONPATH")
$pyexewrap_path = "C:\your\path\here\pyexewrap"
[Environment]::SetEnvironmentVariable("PYTHONPATH", "$PYTHONPATH;$pyexewrap_path")
```
or a cmd command (not recommended unless you know what you are doing. **I don't recommend this since I did not test it!**:
```commandline
setx /M PYTHONPATH "%PYTHONPATH%;C:\your\path\here\pyexewrap"
```

# Double-click usage (the main purpose of this tool)
Using shebang on the first line of all your new scripts:
```commandline
#!/usr/bin/env/ python -m pyexewrap
```
Your .py file extensions must be associated with the Windows Python Launcher (C:\Windows\py.exe) which comes with any Python installer downloaded from the official python website.
It appears that you may not have py.exe installed if your Python has been installed from the Windows Store.
Contrary to python.exe, py.exe has the ability to read shebang lines with "virtual commands".
More info here: https://python.readthedocs.io/en/latest/using/windows.html#shebang-lines

Then the file (the "enhanced script") can be double-clicked. It will have the specified behaviour.
See the provided example scripts for a better understanding.

Option : The enhanced script can also be setup to only stop in case of exception and flash the console otherwise.
This is done by setting a global variable that will be checked at the wrapper level. Just add this line at the end of the script:
```commandline
globals()['pyexewrap_mustpause_in_console'] = False
```

# CLI (command line interface) usage
This has no added value at the moment (unless you modify the wrapper to inject other features than the pausing message):
```commandline
python -m pyexewrap <myscript.py>
```

# Todo / Side effect
1) Since the script is run from the location of pyexewrap, any scripts using paths relative to the current script location will fail. There should be a way to improve this.

2) Since the script to be wrapped is read then executed by pyexewrap.__main__.main() the exceptions occuring at the top level of the script won't be displayed exactly like they would have been otherwise.
 tips here for an improvement: https://stackoverflow.com/questions/47183305/file-string-traceback-with-line-preview

# Contributions
I am a newbie to python. Your contributions would be greatly appreciated. Feel free to copy the project.

