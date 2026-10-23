"""
CLI Contract Conformance Tests for gpower-clone
Course: YZM301 Software Verification and Testing - Teardown Sprint
Tests version query, missing parameters, unknown parameters, output format.
"""

import subprocess
import sys
import json
import pytest

PYTHON_EXE = sys.executable


def run_cli_cmd(args):
    cmd = [PYTHON_EXE, "-m", "src.cli"] + args
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def test_cli_version():
    code, stdout, _ = run_cli_cmd(["--version"])
    assert code == 0
    data = json.loads(stdout)
    assert data["contract_version"] == "1.0.0"
    assert "name" in data
    assert "engine" in data


def test_cli_missing_parameter():
    # Missing --ratio in a-priori
    code, stdout, _ = run_cli_cmd(["--test", "t2-indep", "--mode", "a-priori", "--tails", "1", "--d", "0.5", "--alpha", "0.05", "--power", "0.95"])
    assert code == 2
    data = json.loads(stdout)
    assert "error" in data
    assert data["code"] == "MISSING_PARAM"
    assert data["field"] == "ratio"


def test_cli_unknown_parameter():
    # Disallowed --power in post-hoc mode
    code, stdout, _ = run_cli_cmd(["--test", "t2-indep", "--mode", "post-hoc", "--tails", "1", "--d", "0.5", "--alpha", "0.05", "--n1", "50", "--n2", "50", "--power", "0.95"])
    assert code == 2
    data = json.loads(stdout)
    assert "error" in data
    assert data["code"] == "UNKNOWN_PARAM"


def test_cli_unsupported_test():
    code, stdout, _ = run_cli_cmd(["--test", "unknown-test", "--mode", "a-priori"])
    assert code == 2
    data = json.loads(stdout)
    assert data["code"] == "UNSUPPORTED"


def test_cli_success_single_line_json():
    code, stdout, _ = run_cli_cmd(["--test", "t2-indep", "--mode", "a-priori", "--tails", "1", "--d", "0.5", "--alpha", "0.05", "--power", "0.95", "--ratio", "1"])
    assert code == 0
    assert "\n" not in stdout, "Output must be single line JSON"
    data = json.loads(stdout)
    assert isinstance(data["n1"], int)
    assert isinstance(data["n2"], int)
    assert isinstance(data["n_total"], int)
    assert isinstance(data["df"], int)
    assert isinstance(data["actual_power"], float)
