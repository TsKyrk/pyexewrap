import os
import sys
import traceback

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
            exec(script_code)

            if pyexewrap_verbose: print("pyexewrap_mustpause_in_console="+str(pyexewrap_mustpause_in_console))

        except Exception as e:
            print(f"Error executing {script_to_execute}: {type(e).__name__}")
            print(traceback.format_exc())
            print("This exception has ended the script before the end.")

    if pyexewrap_verbose: print("pyexewrap ended.")

    # The windows environment variable PROMPT only exists when there is an active console
    if (not 'PROMPT' in os.environ) and pyexewrap_mustpause_in_console:
        # Pausing the script to let the user read stdout and/or strerr before the window gets closed
        wait = input("Press Enter to continue.")

if __name__ == "__main__":
    main()
