import os
import sys
import traceback
import code

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
    # pyexewrap_verbose = True # Uncomment to debug with verbose mode
    if not 'pyexewrap_verbose' in locals(): pyexewrap_verbose = False
    
    if pyexewrap_verbose: print("pyexewrap activated.")

    if len(sys.argv) < 2: 
        print("Usage: python wrap.py <script.py>")
    else:
        try:
            if pyexewrap_verbose: print("interpreter is " + sys.executable)
            if pyexewrap_verbose: print("CLI is " + " ".join(sys.argv))
            
            script_to_execute = sys.argv[1]
            with open(script_to_execute, 'r') as f: script_code = f.read()

            # This global variable can be changed by the executed scripts
            global pyexewrap_mustpause_in_console
            pyexewrap_mustpause_in_console = True

            # Execute the script code within the current context
            # note that globals are also binded to exec's locals. This is mandatory : see the unitary test E001.
            code = compile(script_code,script_to_execute,"exec")
            exec(code, globals(), globals())

            if pyexewrap_verbose: print("pyexewrap_mustpause_in_console="+str(pyexewrap_mustpause_in_console))

        except Exception as e:
            # These 2 lines are now replaced by showtraceback():
            # print(f"Error executing {script_to_execute}: {type(e).__name__}")
            # print(traceback.format_exc())
            showtraceback()
            print("This exception has ended the script before the end.")

    if pyexewrap_verbose: print("pyexewrap ended.")

    # The windows environment variable PROMPT only exists when there is an active console
    if (not 'PROMPT' in os.environ) and pyexewrap_mustpause_in_console:
        # Pausing the script to let the user read stdout and/or strerr before the window gets closed
        while True:
            wait = input("Press <Enter> to continue and quit. (c+<Enter> for cmd console.) (i+<Enter> for interactive python console.)\n")
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
                #os.system("python")
                try:
                    code.interact(local=globals())
                except BaseException as e:
                    print(traceback.format_exc())
                print("\n")
            else:
                sys.exit()

if __name__ == "__main__":
    main()
