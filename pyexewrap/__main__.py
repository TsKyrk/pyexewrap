import os
import sys
import traceback
import code

# Main function of the pyexewrap package
def main():
    if not 'pyexewrap_verbose' in locals():
        pyexewrap_verbose = False
    
    if pyexewrap_verbose: print("pyexewrap activated.")

    if len(sys.argv) < 2:
        print("Usage: python wrap.py <script.py>")

    else:
        try:
            if pyexewrap_verbose: print("interpreter is "+sys.executable)
            if pyexewrap_verbose: print("CLI is "+" ".join(sys.argv))
            
            script_to_execute = sys.argv[1]
            with open(script_to_execute, 'r') as f:
                script_code = f.read()

            #This global variable can be changed by the executed scripts
            global pyexewrap_mustpause_in_console
            pyexewrap_mustpause_in_console = True

            # Execute the script code within the current context
            # note that globals are also binded to exec's locals. This is mandatory : see the unitary test E001.
            exec(script_code, globals(), globals())

            if pyexewrap_verbose: print("pyexewrap_mustpause_in_console="+str(pyexewrap_mustpause_in_console))

        except Exception as e:
            print(f"Error executing {script_to_execute}: {type(e).__name__}")
            print(traceback.format_exc())
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
