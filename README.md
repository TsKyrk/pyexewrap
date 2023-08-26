# What is pyexewrap ?
pyexewrap is a tool for those who don't want to run scripts typing command line in a console but through double-clicks in the Windows file explorer.
Usually, when a .py file is double-clicked, the script will pop a console that will most likely flash away from the user's screen unless the last line of code has some blocking command like 
```commandline
input("Press ENTER to continue")
```
Even then, if an exception occurs, which is common in development phase, the console will still flash away.
Moreover, if the same script is run from the command line interface or is called by another script, this additional blocking line becomes undesirable.

Pyexewrap is a tool that can be used to enhance (wrap) other python scripts just by adding the proper shebang line on their first line.
On the enhanced scripts, the pausing message "Press <Enter> to continue." will automatically show up but only if the script is directly double-clicked, not when it is called or launched through CLI.
Most importantly, the pausing message will appear even if an exception occurs before the last line of code which will enable a quick debugging of the exception.

Bonus feature #1: it is possible to launch an interactive python console at the end of the script by pressing i+<Enter> once prompted. This python console will keep all the local variables of the script that has just run. This is useful for instance to debug the script interactively by digging into variables.

Bonus feature #2: it is possible to launch a cmd console at the end of the script by pressing c+<Enter> once prompted. This is useful for instance to lauch a proper "pip install xxx" command as a result of a "module not found" exception.

Bonus feature #3: for double-clicked scripts the usual title "py.exe" is replaced with a more explicit one showing the script name being run. This is usefull to distinguish the various script windows that are running simultaneously.

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
This has no added value at the moment (unless you modify the wrapper to inject other features than the automatic pausing message at the end of the script):
```commandline
python -m pyexewrap <myscript.py>
```

# Todo / Side effect
None to my knowledge. All the knwon side effects have been fixed.

# Contributions
I am a newbie to python. Your contributions would be greatly appreciated. Feel free to copy the project.

