"""Display the winpyfiles file association diagnosis."""
import sys
import os

# Allow running directly from this folder without installing the packages.
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from winpyfiles.__main__ import cmd_diagnose


def main():
    cmd_diagnose()

    if _is_double_clicked():
        input("\nPress Enter to close...")


def _is_double_clicked():
    return len(sys.argv) == 1 and sys.stdin and sys.stdin.isatty()


if __name__ == "__main__":
    main()
