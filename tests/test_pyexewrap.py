"""Automated regression tests for pyexewrap.

These tests verify the core behavior of the tool and protect against regressions.
For interactive ergonomic tests demonstrating the tool's UX, see unit_tests/.
"""
import os
import pytest
from pyexewrap.__main__ import run_script


@pytest.fixture(autouse=True)
def cli_mode(monkeypatch):
    """Simulate CLI execution (not double-click) for all tests.

    This prevents run_script() from blocking on input() at the pause prompt.
    Tests that need to simulate a double-click override this fixture.
    """
    monkeypatch.setenv("PROMPT", ">")
    monkeypatch.delenv("pyexewrap_simulate_doubleclick", raising=False)


# ---------------------------------------------------------------------------
# Basic execution
# ---------------------------------------------------------------------------

def test_simple_script_runs(tmp_path, capsys):
    """A basic script executes and produces the expected output."""
    script = tmp_path / "hello.py"
    script.write_text('print("hello world")', encoding="utf-8")

    pause = run_script(str(script))

    assert capsys.readouterr().out.strip() == "hello world"
    assert pause is False  # no pause in CLI mode


def test_no_pause_in_cli_mode(tmp_path):
    """run_script() returns False (no pause) when executed from a console."""
    script = tmp_path / "noop.py"
    script.write_text("x = 1", encoding="utf-8")

    assert run_script(str(script)) is False


def test_pause_in_doubleclick_mode(tmp_path, monkeypatch):
    """run_script() returns True (pause needed) when double-clicked."""
    script = tmp_path / "noop.py"
    script.write_text("x = 1", encoding="utf-8")

    monkeypatch.delenv("PROMPT", raising=False)
    monkeypatch.setenv("pyexewrap_simulate_doubleclick", "1")

    assert run_script(str(script)) is True


# ---------------------------------------------------------------------------
# E001 — imports accessible inside functions
# ---------------------------------------------------------------------------

def test_import_accessible_inside_function(tmp_path, capsys):
    """Module-level imports are visible inside functions (E001 regression).

    Before the fix, exec() used different global/local scopes so imports
    made at module level were invisible from within a called function.
    """
    script = tmp_path / "e001.py"
    script.write_text(
        "import os\n"
        "def get_sep():\n"
        "    return os.sep\n"
        "print(get_sep())\n",
        encoding="utf-8",
    )

    run_script(str(script))

    assert capsys.readouterr().out.strip() == os.sep


# ---------------------------------------------------------------------------
# E002 — clean exception traceback (no pyexewrap frame)
# ---------------------------------------------------------------------------

def test_exception_shows_traceback(tmp_path, capsys):
    """An uncaught exception prints the traceback to stdout (E002 regression)."""
    script = tmp_path / "e002.py"
    script.write_text("raise ValueError('oops')", encoding="utf-8")

    run_script(str(script))

    out = capsys.readouterr().out
    assert "ValueError" in out
    assert "oops" in out


def test_traceback_excludes_pyexewrap_frame(tmp_path, capsys):
    """The traceback does not expose pyexewrap's internal exec() frame (E002 regression).

    Before the fix, the traceback started with pyexewrap/__main__.py, which was
    confusing because it didn't belong to the user's script.
    """
    script = tmp_path / "e002_clean.py"
    script.write_text("raise RuntimeError('boom')", encoding="utf-8")

    run_script(str(script))

    out = capsys.readouterr().out
    # The traceback must point to the user's script, not to pyexewrap internals
    assert str(script) in out
    assert "exec(compiled_code" not in out


# ---------------------------------------------------------------------------
# E003 — exit() / quit() / SystemExit handled gracefully
# ---------------------------------------------------------------------------

def test_exit_does_not_crash_pyexewrap(tmp_path):
    """exit() in a script is handled gracefully (E003 regression).

    Before the fix, intercepting SystemExit closed stdin, making the subsequent
    input() in the pause prompt raise ValueError.
    """
    script = tmp_path / "e003_exit.py"
    script.write_text("exit(0)", encoding="utf-8")

    run_script(str(script))  # must not raise


def test_quit_does_not_crash_pyexewrap(tmp_path):
    """quit() in a script is handled gracefully (E003 regression)."""
    script = tmp_path / "e003_quit.py"
    script.write_text("quit(0)", encoding="utf-8")

    run_script(str(script))  # must not raise


def test_systemexit_does_not_crash_pyexewrap(tmp_path):
    """raise SystemExit() in a script is handled gracefully (E003 regression)."""
    script = tmp_path / "e003_systemexit.py"
    script.write_text("raise SystemExit(0)", encoding="utf-8")

    run_script(str(script))  # must not raise


# ---------------------------------------------------------------------------
# E004 — __file__ points to the user's script
# ---------------------------------------------------------------------------

def test_dunder_file_points_to_script(tmp_path, capsys):
    """__file__ inside the executed script is the script's own path (E004 regression).

    Before the fix, __file__ resolved to pyexewrap/__main__.py instead of the
    user's script, breaking any script that relied on __file__ for path resolution.
    """
    script = tmp_path / "e004.py"
    script.write_text("print(__file__)", encoding="utf-8")

    run_script(str(script))

    assert capsys.readouterr().out.strip() == str(script)


# ---------------------------------------------------------------------------
# Customization — must_pause_in_console
# ---------------------------------------------------------------------------

def test_must_pause_false_suppresses_pause(tmp_path, monkeypatch):
    """Setting must_pause_in_console=False prevents the pause even in double-click mode."""
    script = tmp_path / "no_pause.py"
    script.write_text(
        "pyexewrap_customizations['must_pause_in_console'] = False\n",
        encoding="utf-8",
    )

    monkeypatch.delenv("PROMPT", raising=False)
    monkeypatch.setenv("pyexewrap_simulate_doubleclick", "1")

    assert run_script(str(script)) is False


def test_exception_forces_pause_despite_customization(tmp_path, monkeypatch, capsys):
    """An uncaught exception overrides must_pause_in_console=False and forces a pause."""
    script = tmp_path / "forced_pause.py"
    script.write_text(
        "pyexewrap_customizations['must_pause_in_console'] = False\n"
        "raise RuntimeError('forced')\n",
        encoding="utf-8",
    )

    monkeypatch.delenv("PROMPT", raising=False)
    monkeypatch.setenv("pyexewrap_simulate_doubleclick", "1")

    assert run_script(str(script)) is True
