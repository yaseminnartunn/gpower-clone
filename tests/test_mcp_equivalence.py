import json
import pytest
from src.cli import main as cli_main
from src.mcp_server import execute_power_analysis_tool
from src.engine import run_power_analysis

TEST_CASES = [
    # A-priori standard 1-tail
    {"test": "t2-indep", "mode": "a-priori", "tails": 1, "d": 0.5, "alpha": 0.05, "power": 0.95, "ratio": 1.0},
    # A-priori 2-tail
    {"test": "t2-indep", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.95, "ratio": 1.0},
    # A-priori unequal ratio
    {"test": "t2-indep", "mode": "a-priori", "tails": 2, "d": 0.6, "alpha": 0.01, "power": 0.90, "ratio": 1.5},
    # Post-hoc 1-tail
    {"test": "t2-indep", "mode": "post-hoc", "tails": 1, "d": 0.5, "alpha": 0.05, "n1": 88, "n2": 88},
    # Post-hoc 2-tail unequal
    {"test": "t2-indep", "mode": "post-hoc", "tails": 2, "d": 0.4, "alpha": 0.05, "n1": 50, "n2": 75},
    # Compromise
    {"test": "t2-indep", "mode": "compromise", "tails": 1, "d": 0.5, "beta_alpha_ratio": 1.0, "n1": 88, "n2": 88},
    # Criterion
    {"test": "t2-indep", "mode": "criterion", "tails": 1, "d": 0.5, "power": 0.95, "n1": 88, "n2": 88},
    # Sensitivity
    {"test": "t2-indep", "mode": "sensitivity", "tails": 1, "alpha": 0.05, "power": 0.95, "n1": 88, "n2": 88},
]


def test_mcp_cli_parity():
    """Verify that MCP execute_power_analysis_tool output is 100% equivalent to engine result."""
    for case in TEST_CASES:
        mcp_res = execute_power_analysis_tool(case)
        assert not mcp_res["isError"], f"MCP failed on {case}"
        mcp_json = json.loads(mcp_res["content"][0]["text"])

        engine_res = run_power_analysis(case)
        for k in mcp_json:
            assert k in engine_res
            val1 = mcp_json[k]
            val2 = engine_res[k]
            if isinstance(val1, int):
                assert val1 == int(round(val2))
            else:
                assert abs(val1 - val2) <= 1e-6


def test_mcp_error_parity():
    """Verify that invalid inputs produce identical error output structures in MCP."""
    invalid_cases = [
        {"test": "t2-indep", "mode": "a-priori", "tails": 1, "d": 0.5, "alpha": 0.05, "power": 0.04, "ratio": 1.0},
        {"test": "unknown-test", "mode": "a-priori"},
        {"test": "t2-indep", "mode": "post-hoc", "tails": 1, "d": 0.5, "alpha": 0.05, "power": 0.95, "n1": 50, "n2": 50},  # Disallowed param for post-hoc
    ]

    for case in invalid_cases:
        mcp_res = execute_power_analysis_tool(case)
        assert mcp_res["isError"]
        err_obj = json.loads(mcp_res["content"][0]["text"])
        assert "error" in err_obj
        assert "code" in err_obj
