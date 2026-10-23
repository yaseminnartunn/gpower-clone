"""
CLI Interface for gpower-clone
Course: YZM301 Software Verification and Testing - Teardown Sprint
Contract: CONTRACT.md v1.0.0
"""

import sys
import json
from typing import List, Dict, Any
from src.engine import run_power_analysis, EngineError

CONTRACT_VERSION = "1.0.0"
TEAM_NAME = "YZM301-Teardown-Team-K1"
ENGINE_INFO = f"Python {sys.version.split()[0]} (scipy-powered)"

# Allowed parameters per test and mode for t2-indep
MODE_ALLOWED_PARAMS = {
    "a-priori": {"test", "mode", "tails", "d", "alpha", "power", "ratio"},
    "post-hoc": {"test", "mode", "tails", "d", "alpha", "n1", "n2"},
    "compromise": {"test", "mode", "tails", "d", "beta_alpha_ratio", "n1", "n2"},
    "criterion": {"test", "mode", "tails", "d", "power", "n1", "n2"},
    "sensitivity": {"test", "mode", "tails", "alpha", "power", "n1", "n2"},
}

INTEGER_FIELDS = {"tails", "n1", "n2", "n_total", "df", "df1", "df2", "groups", "predictors"}
FLOAT_FIELDS = {"d", "dz", "f", "w", "f2", "alpha", "power", "ratio", "beta_alpha_ratio", "actual_power", "beta", "critical_t", "ncp"}


def format_success_json(data: Dict[str, Any]) -> str:
    """Format dictionary to single-line JSON with explicit integer/float types."""
    formatted = {}
    for k, v in data.items():
        if k in INTEGER_FIELDS:
            formatted[k] = int(round(v))
        elif isinstance(v, (int, float)):
            formatted[k] = float(v)
        else:
            formatted[k] = v
    return json.dumps(formatted, ensure_ascii=False, separators=(',', ':'))


def format_error_json(message: str, code: str, field: str = None) -> str:
    """Format error according to CONTRACT.md specification."""
    err_obj = {
        "error": message,
        "code": code
    }
    if field:
        err_obj["field"] = field
    return json.dumps(err_obj, ensure_ascii=False, separators=(',', ':'))


def parse_arguments(argv: List[str]) -> Dict[str, Any]:
    """Parse command line arguments of form --key value or --version."""
    if len(argv) == 1 and argv[0] == "--version":
        ver_obj = {
            "contract_version": CONTRACT_VERSION,
            "name": TEAM_NAME,
            "engine": ENGINE_INFO
        }
        print(json.dumps(ver_obj, ensure_ascii=False, separators=(',', ':')))
        sys.exit(0)

    params: Dict[str, Any] = {}
    i = 0
    while i < len(argv):
        arg = argv[i]
        if not arg.startswith("--"):
            raise EngineError(f"Unexpected token without '--': {arg}", code="INVALID_VALUE")
        key = arg[2:]
        if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
            raise EngineError(f"Missing value for argument '--{key}'", code="MISSING_PARAM", field=key)
        val_str = argv[i + 1]
        i += 2

        # Parse data type
        if key in INTEGER_FIELDS:
            try:
                # Disallow floats like 88.5 or strings
                if "." in val_str:
                    raise ValueError()
                val = int(val_str)
            except ValueError:
                raise EngineError(f"Field '{key}' must be an integer, got '{val_str}'", code="INVALID_VALUE", field=key)
            params[key] = val
        elif key in FLOAT_FIELDS or key in {"beta_alpha_ratio"}:
            try:
                val = float(val_str)
            except ValueError:
                raise EngineError(f"Field '{key}' must be a float, got '{val_str}'", code="INVALID_VALUE", field=key)
            params[key] = val
        elif key in {"test", "mode"}:
            params[key] = val_str
        else:
            # Stored as is, will be checked for UNKNOWN_PARAM later
            params[key] = val_str

    return params


def main(argv: List[str] = None):
    if argv is None:
        argv = sys.argv[1:]

    try:
        if not argv:
            raise EngineError("No arguments provided. Use --help or provide --test and --mode.", code="MISSING_PARAM")

        params = parse_arguments(argv)

        test = params.get("test")
        mode = params.get("mode")

        if not test:
            raise EngineError("Parameter '--test' is required", code="MISSING_PARAM", field="test")
        if test != "t2-indep":
            raise EngineError(f"Unsupported test family: '{test}'", code="UNSUPPORTED", field="test")

        if not mode:
            raise EngineError("Parameter '--mode' is required", code="MISSING_PARAM", field="mode")

        if mode not in MODE_ALLOWED_PARAMS:
            raise EngineError(f"Unsupported mode: '{mode}'", code="UNSUPPORTED", field="mode")

        # Validate that all given params are known and allowed for this mode
        allowed = MODE_ALLOWED_PARAMS[mode]
        for key in params:
            if key not in allowed:
                raise EngineError(f"Parameter '--{key}' is not recognized or not allowed for mode '{mode}'", code="UNKNOWN_PARAM", field=key)

        # Run computation
        result = run_power_analysis(params)
        print(format_success_json(result))
        sys.exit(0)

    except EngineError as e:
        print(format_error_json(e.message, e.code, e.field))
        exit_code = 1 if e.code == "NO_SOLUTION" else 2
        sys.exit(exit_code)
    except SystemExit:
        raise
    except Exception as e:
        print(format_error_json(f"Internal calculation error: {str(e)}", code="NO_SOLUTION"))
        sys.exit(1)


if __name__ == "__main__":
    main()
