"""System-level environment checks for pyexewrap double-click invocation.

Unlike the unit tests in test_pyexewrap.py (which call run_script() directly
and always pass regardless of Windows file associations), these tests verify
that the *Windows environment* is correctly configured to actually invoke
pyexewrap when a .py file is double-clicked.

These tests can fail due to external system state (MSIX packages, missing
file associations) rather than code bugs. A failure here means pyexewrap
will not be invoked on double-click, even if the unit tests pass.
"""
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
def test_no_msix_python_manager():
    """FAIL if the MSIX Python Manager (Microsoft Store) is installed.

    PythonSoftwareFoundation.PythonManager intercepts .py/.pyw double-clicks
    through Windows App Model activation declared in its AppxManifest.xml.
    This mechanism bypasses ALL registry-based ftype/assoc/shell\\open\\command
    settings -- making pyexewrap completely unreachable on double-click.

    The unit tests (test_pyexewrap.py) still pass because they call run_script()
    directly, without going through the Windows file association chain.

    Resolution: uninstall 'Python Manager' from the Microsoft Store.
    See README.md section 'Known compatibility risk: python/pymanager'.
    """
    pkg = find_msix_python_package()
    if pkg:
        pytest.fail(
            f"\n\n"
            f"  MSIX Python Manager detected:\n"
            f"    {pkg}\n\n"
            f"  This package intercepts .py/.pyw double-clicks via Windows App Model\n"
            f"  activation (AppxManifest.xml), bypassing all ftype/registry settings.\n"
            f"  pyexewrap CANNOT be invoked on double-click while this is installed.\n\n"
            f"  The unit tests still pass because they call run_script() directly --\n"
            f"  they do not go through the Windows file association chain.\n\n"
            f"  Resolution: uninstall 'Python Manager' from the Microsoft Store.\n"
            f"  See README.md 'Known compatibility risk: python/pymanager'."
        )

    handlers = find_python_appx_prog_ids()
    if handlers:
        pytest.fail(
            f"\n\n"
            f"  MSIX AppX Python handlers detected in registry:\n"
            f"    {list(handlers.keys())}\n\n"
            f"  These handlers take priority over ftype settings for .py double-clicks.\n"
            f"  pyexewrap cannot be invoked until the MSIX package is removed.\n"
            f"  See README.md 'Known compatibility risk: python/pymanager'."
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
