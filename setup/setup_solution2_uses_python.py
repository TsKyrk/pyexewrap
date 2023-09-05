import os
import subprocess


def add_path_to_a_windows_environment_variable(my_path : str, env_var : str):
    """
    Adds 'my_path' to the Windows environment variable 'env_var'
    """

    def os_system_stdout(cmd : str):
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True, encoding='cp850')
        if result.returncode == 0:
            return result.stdout.strip(), result.returncode
        else:
            return "Error executing the command", result.returncode

    # List of unique paths found in 'env_var'
    current_env_var = os.environ.get(env_var, '')
    existing_paths_in_env_var = set([path.strip("\\") for path in current_env_var.split(";")])

    # Check if the parent directory is not already in 'env_var'
    if my_path not in existing_paths_in_env_var:
        new_env_var = current_env_var + ";" + my_path if current_env_var else my_path
        print("env_var=" + env_var + "\n" + "new_env_var=" + new_env_var)
        system_msg, rcode = os_system_stdout('setx /M ' + env_var + ' "' + new_env_var + '"')
        if rcode == 0:
            print(system_msg)
            print("Updated " + env_var + " successfuly.")
        else:
            print("Updating failed. Try running this script as an administrator.")
    else:
        print("The path '" + my_path + "' is already in " + env_var + ".")

if __name__ == "__main__":
    # Get the parent folder path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Add it to the PYTHONPATH
    add_path_to_a_windows_environment_variable(parent_dir, "PYTHONPATH")
