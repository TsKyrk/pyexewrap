"""Run all automated tests and display results."""
import subprocess
import sys
import os


def _find_python():
    """Return 'py' if available, otherwise fall back to the current interpreter."""
    try:
        subprocess.run(["py", "--version"], capture_output=True, check=True)
        return "py"
    except (FileNotFoundError, subprocess.CalledProcessError):
        return sys.executable


def main():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    result = subprocess.run(
        [_find_python(), "-m", "pytest", "tests/", "-v"],
        cwd=repo_root,
    )
    print(f"\nExit code: {result.returncode}")

    if _is_double_clicked():
        input("\nPress Enter to close...")


def _is_double_clicked():
    return len(sys.argv) == 1 and sys.stdin and sys.stdin.isatty()


if __name__ == "__main__":
    main()
