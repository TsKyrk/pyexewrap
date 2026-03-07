"""Run all automated tests and display results."""
import subprocess
import sys
import os


def main():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    result = subprocess.run(
        ["py", "-m", "pytest", "tests/", "-v"],
        cwd=repo_root,
    )
    print(f"\nExit code: {result.returncode}")

    if _is_double_clicked():
        input("\nPress Enter to close...")


def _is_double_clicked():
    return len(sys.argv) == 1 and sys.stdin and sys.stdin.isatty()


if __name__ == "__main__":
    main()
