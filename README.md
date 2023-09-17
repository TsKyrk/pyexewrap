# What is pyexewrap ?
pyexewrap is a tool for those who don't want to run scripts typing command lines in a console but through double-clicks in the Windows file explorer.

## Python's native problems for Windows users
- When a .py file is double-clicked, the script will pop a console that will most likely flash away from the user's screen unless the last line of code has some blocking command like 
`input("Press ENTER to continue")`
- Even then, if an exception occurs, which is common in development phase - think of syntax errors for example - the console will still flash away forcing you to switch to console mode to read the traceback.

- If the same script is run from the command line interface or is called by another script (python or batch), this additional blocking line usually becomes undesirable.

- When a python scripts uses .pyw extension, there is no chance to read the traceback post-mortem since the console windows is natively hidden.

## Main features 
1. Pyexewrap is a tool that can be used to enhance (wrap) other python scripts. On these enhanced scripts, a pausing message "Press <Enter> to continue." will automatically show up but only if the script is launched through a double-click, but not when it is called by another script or launched through CLI.

1. Most importantly, on an enhanced script the pausing message will appear even if an exception occurs before the last line of code which will enable a quick post-mortem debugging of the exceptions without needing to re-run scripts from a console to read the lost useful messages.

1. For enhanced .pyw scripts (windowed no console Python scripts) in case of uncaught exception that crashes the execution, the console will be displayed with a pausing message so that the user can see the usefull traceback. The user will have to find his own "tricks" to access the useful traceback on these files.

## Bonus features
1. The pausing message enables launching an interactive python console at the end of the script by pressing i+\<Enter\> once prompted. This python console will keep all the local variables of the script that has just run. This is useful for instance to debug the script interactively by digging into variables.

1. The pausing message enables launching a cmd console at the end of the script by pressing c+\<Enter\> once prompted. This is useful for instance to launch a proper "pip install xxx" command as a result of a "module not found" exception.

1. Tor double-clicked enhanced scripts the default windows title "py.exe" is replaced with a more explicit one showing the script name being run. This is useful to distinguish the various script windows that are running simultaneously.

## Notes
- py.exe is already the Windows wrapper for multiple python interpreters. This makes pyexewrap a wrapper of a wrapper. We could wish that someday py.exe will directly implement the features of this tool so that the use of pyexewrap could be deprecated.

# Installation and updates on your machine
Git-clone this repo "https://github.com/TsKyrk/pyexewrap/" to your local drive or [direct download it as a ZIP](https://github.com/TsKyrk/pyexewrap/archive/refs/heads/main.zip) and unzip it to your desired local drive. 
For example the path to your local copy would look something like "C:\MyRepos\pyexewrap" or "D:\MyRepos\pyexewrap-main" (your choice).
This path shall then be added to your PYTHONPATH environment variable to be visible from any location.
You need to have administrator rights for this.

- This can be done using the Windows GUI (**the recommended way**): see Desktop>Properties>Advanced settings>Environment variables... 

- Or a PowerShell command (not recommended unless you know what you are doing. **I don't recommend this since I did not test it!**:
```commandline
$PYTHONPATH = [Environment]::GetEnvironmentVariable("PYTHONPATH")
$pyexewrap_path = "C:\your\path\here\pyexewrap"
[Environment]::SetEnvironmentVariable("PYTHONPATH", "$PYTHONPATH;$pyexewrap_path")
```
- Or a cmd command (not recommended unless you know what you are doing. **I don't recommend this since I did not test it!**:
```commandline
setx /M PYTHONPATH "%PYTHONPATH%;C:\your\path\here\pyexewrap"
```

That's it. Now the tool can be updated anytime through a git-pull (or a new direct download of the ZIP).

# Command line interface usage (The wrapping CLI)
The command line `python -m pyexewrap <myscript.py>` will run pyexewrap on your scripts. This has no added value at the moment (unless you're aiming for the bonus features of the tool). But this command helps you understand how the tool wraps the other scripts.

# Double-click usage on a script (the main purpose of this tool)
## Enhancing with a shebang + py.exe
As a Windows user you should have py.exe on your machine. Hence your Python scripts can be enhanced using a shebang on the first line of code: `#!/usr/bin/env/ python -m pyexewrap`. Then, once double-clicked, your scripts will behave as mentionned above. Try double-clicking on the example scripts provided in the folder "example_scripts" for a better understanding of the added value of enhancing the scripts. The behaviour of enhanced scripts should remain unchanged if called by other scripts (since only py.exe would read the shebang line of the first clicked script).

**Note #1:** Make sure that your .py file extensions are correctly associated with the Windows Python Launcher (C:\Windows\py.exe): The icon of the application is the Python logo with a rocket on its left. This is the by default configuration of a normal Python installation.

**Note #2:** The Windows Python Launcher comes automatically with any Python installer (Setup.exe) downloaded from the official python website. You can run setup.exe again and use "Modify" to see it in the custom installations. It appears that you may not have py.exe installed if your Python has been installed from the Windows Store: you'll have to [get a Setup.exe from python.org](https://www.python.org/downloads/windows/).

**Note #3:** Contrary to python.exe, py.exe has the ability to read shebang lines with "virtual commands". More info [here]( https://python.readthedocs.io/en/latest/using/windows.html#shebang-lines). pyexewrap is built around this feature.

## Enhancing without a shebang line
You may not want to alter your scripts with a shebang line that will only work on your machine and will crash their execution for other people. For instance you may be sharing those scripts on a repo or a network folder with people who did not setup pyexewrap yet. Then the shebang line can be replaced by a shortcut or a batch file that will implement the wrapping CLI. The two methods are explained hereafter and examples are also provided in the example_scripts folder.

**Using a shortcut:** Create a windows shortcut to the file: ALT+Drag&Drop. Edit the properties of the shortcut (ALT+DoubleClick on Shortcut.lnk). Add the following prefix in the target field : `python -m pyexewrap `. Click OK to save your changes.

**Using a batch:** Create a new file MyFile.bat and edit it with a text editor:
```commandline
@echo off
set pyexewrap_simulate_doubleclick=1
python -m pyexewrap "C:\...\your target script with spaces in the name.py"
```

**Note #1:** Without the shebang line the tool kinda looses its added value and the workflow is not quite sexy. If you have 20 scripts to enhance you'll have to create wrapper batch or wrapper shortcuts for each one of them to make them running with the enhanced behaviours. See the TODO paragraph for ideas of improvements under consideration.

**Note #2:** The batch method allows relative paths so the batch can be placed in the same folder.

## Option to not pause (unless an exception occurs)
An enhanced script can also be setup to only stop in case of uncaught exception and flash away otherwise.
This is done by setting a global variable that will be checked at the wrapper level. Just add this line anywhere in your script (preferably at the end):
```commandline
globals()['pyexewrap_mustpause_in_console'] = False
```

# Useful tricks
**Icons:** All the scripts launched using pyexewrap will show the Windows Python Launcher icon. A simple solution to use customized icons for your scripts is to create a shortcut to the script and edit its properties to define the custom icon. See the example provided in the "example scripts" folder.

# Side effects and bugs
<!-- None to my knowledge. All the known side effects have been fixed. Please report any bug or side effects you may find. -->
- exit()/quit() commands in python closes stdin. To prevent this, __builtins__.exit() and __builtins__.quit() have been monkey-patched which might have side effects.
- pyexewrap is not compatible with Python 3.8.10 due to dict mergin using | operator. This could be removed.

# Todos
- Implement an installer for an easy deployment of the tool. Maybe upload the tool to Pypi?
- Define a system-level switch (environment variable?) to set or unset pyexewrap as a default bahaviour that will apply even to the scripts that are not enhanced with a shebang.
- Setup a context menu item "Run with pyexewrap" to allow using the tool on script that is not enhanced with a shebang line.
- Setup a context menu item "Bypass pyexewrap" to allow bypassing the tool on script that is not enhanced with a shebang line (no added value at the moment imo).
- Automate unit tests so that the tool could be tested agains multiple versions of python.
- Add a version number (no added value at the moment imo).
- Get rid of the (ugly) monkey-patching fix
- Fix compatibility issue with Python 3.8.10 (stop using | for merging dicts)
- Test the tool with older versions of python

# Contributions
I am a newbie to python. Your contributions would be greatly appreciated. Feel free to copy the project.

