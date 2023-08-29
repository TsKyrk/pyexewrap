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
    Display the exception that just occurred. But first we remove the first stack item because it is our own code.
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


# Main function of the pyexewrap package
def main():
    # pyexewrap_verbose = True  # Uncomment to debug with verbose mode
    if 'pyexewrap_verbose' not in locals(): pyexewrap_verbose = False
    if 'pyexewrap_must_change_title' not in locals(): pyexewrap_must_change_title = True
    
    if pyexewrap_verbose: print("pyexewrap activated.")

    if len(sys.argv) < 2: 
        print("Usage: python wrap.py <script.py>")
    else:
        script_to_execute = sys.argv[1]
        script_extension = os.path.splitext(script_to_execute)[1]

        try:
            if pyexewrap_verbose: 
                print("interpreter is " + sys.executable)
                print("CLI is " + " ".join(sys.argv))
                print("script extension is " + script_extension)
            
            # .pyw files should have a hidden console unless an exception occurs
            if script_extension == ".pyw":
                User32.show_window(User32.Const.SW_HIDE)  # Use SW_SHOWMINIMIZED to debug
            
            # The windows environment variable PROMPT only exists when there is an active console
            # if not run in console (but with py.exe through double-click) the window title will be explicit
            if ('PROMPT' not in os.environ) and pyexewrap_must_change_title:
                os.system("title " + os.path.basename(script_to_execute) + " -- pyexewrap " + script_to_execute)
            
            with open(script_to_execute, 'r') as f: script_code = f.read()

            # This global variable can be changed by the executed scripts
            global pyexewrap_must_pause_in_console
            pyexewrap_must_pause_in_console = True

            # Execute the script code within the current context
            # note that globals are also binded to exec's locals. This is mandatory : see the unitary test E001.
            compiled_code = compile(script_code, script_to_execute, "exec")
            exec(compiled_code, globals(), globals())

            if pyexewrap_verbose: print("pyexewrap_must_pause_in_console="+str(pyexewrap_must_pause_in_console))

        except Exception as e:
            if script_extension == ".pyw":
                # From now on pyexewrap will consider the script as a .py file (with a pausing message to display)
                script_extension = ".py"
                User32.show_window(User32.Const.SW_SHOWDEFAULT)
            # These 2 lines are now replaced by showtraceback():
            # print(f"Error executing {script_to_execute}: {type(e).__name__}")
            # print(traceback.format_exc())
            showtraceback()
            print("This exception has ended the script before the end.")

    if pyexewrap_verbose: print("pausing message ?")

    # PAUSING MESSAGE AT THE END OF THE SCRIPT
    # The windows environment variable PROMPT only exists when there is an active console
    if ('PROMPT' not in os.environ) and pyexewrap_must_pause_in_console and script_extension != ".pyw":
        # Pausing the script to let the user read stdout and/or strerr before the window gets closed
        while True:
            wait = input("Press <Enter> to continue and quit."
                         " (c+<Enter> for cmd console.) (i+<Enter> for interactive python console.)\n")
            if wait.lower() == "c":
                print('Opening a windows console (cmd.exe). Type "exit" to quit.\n\n')
                try:
                    os.system("cmd /k")
                except KeyboardInterrupt:
                    # For some reason Ctrl+C used in cmd console are raised again after returning. So we just pass it.
                    pass
                except BaseException as e:
                    # Just in case there are other exceptions to catch
                    print(traceback.format_exc())
                print("\n")
            elif wait.lower() == "i":
                print('Opening python interactive console (python.exe). Type "Ctrl+Z to quit.\n\n')
                # os.system("python")
                try:
                    code.interact(local=globals())
                except BaseException as e:
                    print(traceback.format_exc())
                print("\n")
            else:
                break  # exits while True to end pyexewrap
    
    if pyexewrap_verbose: print("pyexewrap ended.")
    sys.exit()


if __name__ == "__main__":
    main()
