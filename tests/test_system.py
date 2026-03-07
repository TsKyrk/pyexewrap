"""System-level environment checks for pyexewrap double-click invocation.

Unlike the unit tests in test_pyexewrap.py (which call run_script() directly
and always pass regardless of Windows file associations), these tests verify
that the *Windows environment* is correctly configured to actually invoke
pyexewrap when a .py file is double-clicked.

These tests can fail due to external system state (MSIX packages, missing
file associations) rather than code bugs. A failure here means pyexewrap
will not be invoked on double-click, even if the unit tests pass.

MSIX Python Manager compatibility:
  The shebang approach (#!/usr/bin/env python -m pyexewrap) works correctly
  with the MSIX launcher. Only ByDefaultActivation (registry ftype changes)
  is blocked by MSIX. See MSIX_COMPATIBILITY.md for details.
"""
import warnings
import pytest

try:
    from winpyfiles._assoc import diagnose, find_msix_python_package, find_python_appx_prog_ids
    HAS_WINPYFILES = True
except ImportError:
    HAS_WINPYFILES = False

_winpyfiles = pytest.mark.skipif(
    not HAS_WINPYFILES,
    reason="winpyfiles not importable (add repo root to PYTHONPATH)"
)


@_winpyfiles
def test_msix_python_manager_shebang_compatible():
    """WARN (not fail) if the MSIX Python Manager is installed.

    The MSIX launcher includes its own py.exe that reads shebang lines, so
    the shebang approach (#!/usr/bin/env python -m pyexewrap) works correctly
    with the MSIX Python Manager. This has been confirmed by double-click testing.

    What does NOT work with MSIX:
      ByDefaultActivation (registry ftype changes via winpyfiles/activate.py)
      are silently ignored by the App Model activation.

    See MSIX_COMPATIBILITY.md for the full compatibility matrix.
    """
    pkg = find_msix_python_package()
    handlers = find_python_appx_prog_ids()

    if pkg or handlers:
        warnings.warn(
            f"\n\n"
            f"  MSIX Python Manager detected: {pkg or '(package path unknown)'}\n\n"
            f"  Shebang approach (#!/usr/bin/env python -m pyexewrap): works correctly.\n"
            f"  ByDefaultActivation (registry ftype via winpyfiles): does NOT work --\n"
            f"  registry changes are bypassed by the App Model activation.\n\n"
            f"  See MSIX_COMPATIBILITY.md for details.",
            UserWarning,
            stacklevel=2,
        )


@_winpyfiles
def test_py_ftype_command_references_pyexewrap():
    """The Windows ftype command for .py/.pyw files must reference pyexewrap.

    This test is automatically skipped when the MSIX Python Manager is
    detected (since in that case the ftype command is bypassed anyway --
    see test_no_msix_python_manager for the root cause).
    """
    if find_msix_python_package() or find_python_appx_prog_ids():
        pytest.skip(
            "MSIX Python Manager detected -- ftype command is bypassed by "
            "App Model activation. See test_no_msix_python_manager."
        )

    d = diagnose()
    for ext_info in d.extensions:
        pid = ext_info.user_choice or ext_info.prog_id_effective
        if not pid:
            pytest.fail(
                f"{ext_info.extension}: no ProgID configured -- extension is unmapped.\n"
                f"Run 'py -m winpyfiles diagnose' then 'py tools/ByDefaultActivation/activate.py'."
            )
        info = d.prog_ids.get(pid)
        cmd = info.command_effective if info else None
        assert cmd and "pyexewrap" in cmd.lower(), (
            f"{ext_info.extension}: pyexewrap not found in the ftype command.\n"
            f"  ProgID  : {pid}\n"
            f"  Command : {cmd!r}\n\n"
            f"Run 'py -m winpyfiles diagnose' for full details, then\n"
            f"'py tools/ByDefaultActivation/activate.py' to configure."
        )
