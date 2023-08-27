# What is pyexewrap ?
pyexewrap is a tool for those who don't want to run scripts typing command lines in a console but through double-clicks in the Windows file explorer.

**The problem to solve:** Usually, when a .py file is double-clicked, the script will pop a console that will most likely flash away from the user's screen unless the last line of code has some blocking command like 
```commandline
input("Press ENTER to continue")
```
Even then, if an exception occurs, which is common in development phase (think of syntax errors for example), the console will still flash away forcing you to switch to console mode to read the traceback.

Moreover, if the same script is run from the command line interface or is called by another script (python or batch), this additional blocking line usually becomes undesirable.

**Main feature #1:** Pyexewrap is a tool that can be used to enhance (wrap) other python scripts just by adding the proper shebang line on their first line.

On these enhanced scripts, the pausing message "Press <Enter> to continue." will automatically show up but only if the script is directly double-clicked, not when it is called or launched through CLI. 

**Main feature #2:** Most importantly, the pausing message will appear even if an exception occurs before the last line of code which will enable a quick debugging of the exceptions without needing to re-run scripts from a console to read the lost useful messages.

**Bonus feature #1:** the pausing message enables launching an interactive python console at the end of the script by pressing i+\<Enter\> once prompted. This python console will keep all the local variables of the script that has just run. This is useful for instance to debug the script interactively by digging into variables.

**Bonus feature #2:** the pausing message enables launching a cmd console at the end of the script by pressing c+\<Enter\> once prompted. This is useful for instance to launch a proper "pip install xxx" command as a result of a "module not found" exception.

**Bonus feature #3:** for double-clicked scripts the default windows title "py.exe" is replaced with a more explicit one showing the script name being run. This is useful to distinguish the various script windows that are running simultaneously.

**Note:** py.exe is already the Windows wrapper for multiple python interpreters. This makes pyexewrap a wrapper of a wrapper. We could wish that someday py.exe will directly implement the features of this tool so that the use of pyexewrap could be deprecated.

# Installation and updates
Git-clone this repo "https://github.com/TsKyrk/pyexewrap/" to your local drive or [direct download it as a ZIP](https://github.com/TsKyrk/pyexewrap/archive/refs/heads/main.zip) and unzip it to your desired local drive. 
For example the path to your local copy would look something like "C:\MyRepos\pyexewrap" or "D:\MyRepos\pyexewrap-main" (your choice).
This path shall then be added to your PYTHONPATH environment variable to be visible from any location.
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

That's it. Now the tool can be updated anytime through a git-pull (or a new direct download of the ZIP).

# Double-click usage (the main purpose of this tool)
**Main usage:** Your scripts should be "enhanced" using the following shebang on the first line of code:
```commandline
#!/usr/bin/env/ python -m pyexewrap
```
Then the "enhanced script", once double-clicked, will behave the specified above. Try double-clicking on the example scripts provided in the folder "example_scripts" for a better understanding of the added value of the tool.

**Note #1:** Make sure that your .py file extensions are correctly associated with the Windows Python Launcher (C:\Windows\py.exe): The icon of the application is the Python logo with a rocket on its left.

**Note #2:** The Windows Python Launcher comes automatically with any Python installer (Setup.exe) downloaded from the official python website. You can run setup.exe again and use "Modify" to see it in the custom installations. It appears that you may not have py.exe installed if your Python has been installed from the Windows Store: you'll have to [get a Setup.exe from python.org](https://www.python.org/downloads/windows/).

**Note #3:** Contrary to python.exe, py.exe has the ability to read shebang lines with "virtual commands". More info [here]( https://python.readthedocs.io/en/latest/using/windows.html#shebang-lines). pyexewrap is built around this feature.

**Optional usage:** The enhanced script can also be setup to only stop in case of exception and flash away otherwise.
This is done by setting a global variable that will be checked at the wrapper level. Just add this line at the end of your script:
```commandline
globals()['pyexewrap_mustpause_in_console'] = False
```

# CLI (command line interface) usage
The following command will run pyexewrap on your scripts exactly like the shebang line would do:
```commandline
python -m pyexewrap <myscript.py>
```
but this has no added value at the moment (unless you modify the tool yourself to inject other features).

**Note #1:** It could be interesting to setup a context menu item "Run with pyexewrap" to allow using the tool on script that is not enhanced with a shebang line.

# Useful tricks
**Icons:** All the scripts launched using pyexewrap will show the Windows Python Launcher icon. A simple solution to use customized icons for your scripts is to create a shortcut to the script and edit its properties to define the custom icon. See the example provided in the "example scripts" folder.

# Side effects and bugs
None to my knowledge. All the known side effects have been fixed. Please report any bug or side effects you may find.

# Todos
- Manage .pyw extensions and their annoying behavior with exceptions
- Implement an installer for an easy deployment of the tool. Maybe add the tool to Pypi?
- Automate unit tests (no added value at the moment imo)
- Add a version number (no added value at the moment imo)

# Contributions
I am a newbie to python. Your contributions would be greatly appreciated. Feel free to copy the project.

