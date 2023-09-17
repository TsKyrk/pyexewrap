import os
import sys
import traceback
import code

class User32:
    class Const:
        SW_HIDE = 0
        SW_SHOWNORMAL = 1
        SW_SHOWMINIMIZED = 2
        SW_SHOWMAXIMIZED = 3
        SW_SHOWNOACTIVATE = 4
        SW_SHOW = 5
        SW_MINIMIZE = 6
        SW_SHOWMINNOACTIVE = 7
        SW_SHOWNA = 8
        SW_RESTORE = 9
        SW_SHOWDEFAULT = 10
        SW_FORCEMINIMIZE = 11
    
    @staticmethod
    def show_window(n_cmd_show):
        """
        Sets the current window's show state. 
        """
        # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow
        import ctypes
        kernel32 = ctypes.WinDLL('kernel32')
        user32 = ctypes.WinDLL('user32')
        h_wnd = kernel32.GetConsoleWindow()
        user32.ShowWindow(h_wnd, n_cmd_show)


# Copied and adapted from Python IDLE's source code here : https://github.com/python/cpython/blob/3.11/Lib/code.py#L131
# see https://github.com/python/cpython/blob/3.11/LICENSE
# Maybe I could have somehow imported and used InteractiveInterpreter class from cpython/Lib/code.py instead ?
def showtraceback():
    """
    Displays the exception that just occurred. But first we remove the first stack item because it is our own code.
    """
    sys.last_type, sys.last_value, last_tb = ei = sys.exc_info()
    sys.last_traceback = last_tb
    try:
        lines = traceback.format_exception(ei[0], ei[1], last_tb.tb_next)
        if sys.excepthook is sys.__excepthook__:
            print(''.join(lines))
        else:
            # If someone has set sys.excepthook, we let that take precedence
            # over our print
            sys.excepthook(ei[0], ei[1], last_tb)
    finally:
        last_tb = ei = None

def display_pause_prompt_and_menu():
    """
    Pauses a script to let the user read stdout and/or strerr before the window gets closed
    """
    # Looping on the pause message as long as it is needed
    while True:
        wait = None
        # Managing KeyboardInterrupt during the pausing message
        while wait is None:
            try:
                wait = input("Press <Enter> to Quit. (<c> for cmd console. <i> for interactive python. <r> to restart.)\n")
            except KeyboardInterrupt:
                pass  # The menu cannot be left using KeyboardInterrupt
            except:
                print(traceback.format_exc())  # Unexpected exception
        
        # By default, the script is set to end after we break out of the "While True" loop displaying the pausing message
        must_run_script_again = False
        if wait.lower() == "c":
            print('Opening a windows console (cmd.exe). Type "exit" to quit.\n\n')
            try:
                os.system("cmd /k")
            except KeyboardInterrupt:
                pass
            except:
                print(traceback.format_exc())  # Unexpected exception
            print("\n")
        elif wait.lower() == "i":
            print('Opening python interactive console (python.exe). Type "Ctrl+Z to quit.\n\n')
            try:
                code.interact(local=globals())
            except KeyboardInterrupt:
                pass
            except:
                print(traceback.format_exc())  # Unexpected exception
            print("\n")
        elif wait.lower() == "r":
            os.system("cls")
            must_run_script_again = True
            break
        elif wait.lower() == "debug":
            # Secret menu item to help developping new features
            print("place any variable here to debug it: " + sys.executable)
        elif wait.lower() == "pyexewrap":
            # Secret feature to open the tool and start editing the source for new cool features
            os.system("explorer " + os.path.split(sys.argv[0])[0])
        elif wait.lower() == "":
            must_run_script_again = False
            break  # exits while True to end pyexewrap
        else:
            # The commands must be typed accurately. Must retry...
            wait = None

    # Run after we brake out of the While True loop:
    return must_run_script_again


def run_script(script_to_execute):
    ################ BEHAVIOUR CUSTOMIZATION ######
    pyexewrap_customizations = {}
    pyexewrap_customizations['must_pause_in_console'] = True  # This can be changed dynamicaly by the enhanced scripts
    pyexewrap_must_change_title = True
    pyexewrap_verbose = False
    # pyexewrap_verbose = True  # Uncomment to debug with verbose mode

    if pyexewrap_verbose: print("pyexewrap activated.")

    script_extension = os.path.splitext(script_to_execute)[1]
    script_is_doubleclicked = ('PROMPT' not in os.environ) or ('pyexewrap_simulate_doubleclick' in os.environ)
    # script_is_doubleclicked = True  # Uncomment this to simulate a double-clicked script even though you are using a console

    if "pythonw" in sys.executable:
        err_msg = "Error : pyexewrap should never be running with pythonw.exe !\n" + str(sys.executable) + "\n" + str(sys.argv)
        print(err_msg)
        with open("error.txt", encoding="UTF-8") as f:
            f.write(err_msg)

    try:
        ################ INITIALIZATION ##############
        if pyexewrap_verbose: 
            print("interpreter is " + sys.executable)
            print("CLI is " + " ".join(sys.argv))
            print("script extension is " + script_extension)
            print("script_is_doubleclicked=" + str(script_is_doubleclicked))
        
        # .pyw files should have a hidden console unless an exception occurs
        if script_extension == ".pyw":
            User32.show_window(User32.Const.SW_HIDE)  # Use SW_SHOWMINIMIZED to debug
        
        # if not run in console (but with py.exe through double-click) the window title will be explicit
        if script_is_doubleclicked and pyexewrap_must_change_title:
            os.system("title " + os.path.basename(script_to_execute) + " -- pyexewrap " + script_to_execute)
        
        with open(script_to_execute) as f:
            script_code = f.read()

        ################ CODE INJECTION ###############
        # I have deprecated the use of code injection since it was creating a shift in the line numbering of the
        # exception tracebacks. One idea could be to inject code only on the first line but it is equivalent to
        # executing a code here first and then use exec().
        # Code _modification_ coulds still be a thing though. For replacing a variable by another or changing paths, etc.
        
        ################ MONKEY PATCHING ####
        # exit() and quit() raise SystemExit but it also closes stdin which is a problem : I don't know how to reopen stdin after that
        # The workaround is to monkey patch exit() and quit() and any other quitter defined here : 
        # https://github.com/python/cpython/blob/add16f1a5e4013f97d33cc677dc008e8199f5b11/Lib/site.py#L400C1-L401C55
        def pyexewrap_quitter(code=None):
            print("exit/quit(" + str(code) + ") ==> be aware tha pyexewrap has put a monkeypatch on exit() and quit()")
            raise SystemExit(code)
        __builtins__.exit = pyexewrap_quitter  # Comment out to disable the monkeypatch
        __builtins__.quit = pyexewrap_quitter  # Comment out to disable the monkeypatch
                
        ################ COMPILATION AND EXECUTION ####
        #https://docs.python.org/3/library/functions.html?highlight=exec#exec

        # We don't want the namespace of the exec(compiled_code) being polluted by the imports and declarations of pyexewrap
        # One option was to make a copy of globals() and remove unwanted imports but I am affraid this would eventually be forgotten for future imports
        # The other option is to cherry-pick the only necessary global variables. This may have side effects as well since new 
        # mandatory global vars may appear in python in a distant future.
        # note that '__file__' key is not set to __file__ but to script_to_execute (see unitary test E004)
        # note that we could identify the list of default global vars of a python execution from unitary test E004 
        globalsParameter = {'__annotations__':__annotations__,
                            '__builtins__' : __builtins__,
                            '__cached__':None,
                            '__doc__':__doc__,
                            '__file__':script_to_execute,
                            '__loader__':__loader__,
                            '__name__':__name__,
                            '__package__':None,
                            '__spec__':__spec__}
        localsParameter = {'pyexewrap_customizations':pyexewrap_customizations}
        compiled_code = compile(script_code, script_to_execute, "exec")
        exec(compiled_code, globalsParameter|localsParameter)

        ##CAN DELETE:
        ## # Too bad I have to do it this way (see above):
        ## globals()['__file__'] = script_to_execute
        ## compiled_code = compile(script_code, script_to_execute, "exec")
        ## exec(compiled_code, globals(), globals())         

        if pyexewrap_verbose: print("must_pause_in_console="+str(pyexewrap_customizations['must_pause_in_console']))

    except SystemExit as e:
        pass
    except BaseException as e:
        pyexewrap_customizations['must_pause_in_console'] = True
        if script_extension == ".pyw":
            # From now on pyexewrap will consider the script as a .py file (with a pausing message to display)
            script_extension = ".py"
            User32.show_window(User32.Const.SW_SHOWDEFAULT)
        # These 2 lines are now replaced by showtraceback():
        # print(f"Error executing {script_to_execute}: {type(e).__name__}")
        # print(traceback.format_exc())
        showtraceback()
        print("This exception has ended the script before the end.")

    pause_decision = script_is_doubleclicked and pyexewrap_customizations['must_pause_in_console'] and script_extension != ".pyw"
    if pyexewrap_verbose: 
        print("pausing message ?")
        print("script_is_doubleclicked=" + str(script_is_doubleclicked))
        print("must_pause_in_console=" + str(pyexewrap_customizations['must_pause_in_console']))
        print("script_extension=" + script_extension)
        print("pause_decision=" + str(pause_decision))

    return pause_decision

# Main function of the pyexewrap package
def main():
    # sys.version_info(major=3, minor=11, micro=3, releaselevel='final', serial=0)
    if sys.version_info.major < 3 or sys.version_info.minor<10:
        print("Warning: pyexewrap has not been tested with Python version 3.9 and below.")
        print("sys.version=" + sys.version)
    
    if len(sys.argv) < 2: 
        print("Usage: python wrap.py <script.py>")
        return
    
    # Looping since the script can be run multiple times
    must_run_script_again = True
    while must_run_script_again:
        
        # But in most cases the script is only run once
        must_run_script_again = False
        
        # The script is run, depending on the situation there should be a pausing prompt
        pause_decision = run_script(sys.argv[1])
        
        # Diplaying the pausing prompt (and defining if the script must be run again)
        if pause_decision:
            must_run_script_again = display_pause_prompt_and_menu()

if __name__ == "__main__":
    main()
