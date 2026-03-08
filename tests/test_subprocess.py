"""Subprocess integration tests for pyexewrap.

These tests invoke pyexewrap as a real subprocess (python -m pyexewrap script.py),
testing the full invocation chain: entry point, double-click detection, output,
pause prompt, and error handling.

Unlike test_pyexewrap.py (which calls run_script() directly in-process), these
tests catch issues in __main__.py's entry point, argument parsing, and process
setup that in-process tests cannot detect.

Double-click is simulated via the pyexewrap_simulate_doubleclick env var.
The pause prompt is dismissed by sending '\\n' to stdin.
"""
import os
import sys
import subprocess
import pytest


def _run(script_path, stdin_input="\n", extra_env=None):
    """Invoke pyexewrap as a subprocess simulating a double-click.

    Returns (stdout, stderr, returncode).
    """
    env = {**os.environ, "pyexewrap_simulate_doubleclick": "1"}
    env.pop("PROMPT", None)
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        [sys.executable, "-m", "pyexewrap", str(script_path)],
        input=stdin_input,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout, result.stderr, result.returncode


# ---------------------------------------------------------------------------
# Basic execution
# ---------------------------------------------------------------------------

def test_subprocess_output_and_pause_prompt(tmp_path):
    """Script output appears and the pause prompt is shown on double-click."""
    script = tmp_path / "hello.py"
    script.write_text('print("hello world")', encoding="utf-8")

    out, _, code = _run(script)

    assert "hello world" in out
    assert "Press <Enter>" in out
    assert code == 0


def test_subprocess_no_pause_in_cli_mode(tmp_path):
    """No pause prompt when invoked from a console (PROMPT env var set)."""
    script = tmp_path / "hello.py"
    script.write_text('print("hello world")', encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "pyexewrap", str(script)],
        capture_output=True,
        text=True,
        env={**os.environ, "PROMPT": ">"},
    )

    assert "hello world" in result.stdout
    assert "Press <Enter>" not in result.stdout
    assert result.returncode == 0


# ---------------------------------------------------------------------------
# Exception handling
# ---------------------------------------------------------------------------

def test_subprocess_exception_shows_traceback(tmp_path):
    """An uncaught exception prints the traceback and then shows the pause prompt."""
    script = tmp_path / "boom.py"
    script.write_text("raise ValueError('subprocess test')", encoding="utf-8")

    out, _, _ = _run(script)

    assert "ValueError" in out
    assert "subprocess test" in out
    assert "Press <Enter>" in out


def test_subprocess_no_pyexewrap_frame_in_traceback(tmp_path):
    """The traceback does not include pyexewrap's internal exec() frame."""
    script = tmp_path / "boom.py"
    script.write_text("raise RuntimeError('clean traceback')", encoding="utf-8")

    out, _, _ = _run(script)

    assert str(script) in out
    assert "exec(compiled_code" not in out


# ---------------------------------------------------------------------------
# Customization
# ---------------------------------------------------------------------------

def test_subprocess_must_pause_false_suppresses_prompt(tmp_path):
    """Setting must_pause_in_console=False suppresses the pause prompt."""
    script = tmp_path / "no_pause.py"
    script.write_text(
        "pyexewrap_customizations['must_pause_in_console'] = False\n"
        'print("done")\n',
        encoding="utf-8",
    )

    out, _, code = _run(script)

    assert "done" in out
    assert "Press <Enter>" not in out
    assert code == 0


def test_subprocess_exception_forces_pause_despite_customization(tmp_path):
    """An uncaught exception overrides must_pause_in_console=False."""
    script = tmp_path / "forced.py"
    script.write_text(
        "pyexewrap_customizations['must_pause_in_console'] = False\n"
        "raise RuntimeError('forced pause')\n",
        encoding="utf-8",
    )

    out, _, _ = _run(script)

    assert "RuntimeError" in out
    assert "Press <Enter>" in out
