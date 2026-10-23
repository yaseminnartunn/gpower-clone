"""
Model Context Protocol (MCP) Server for G*Power Power Analysis
Course: YZM301 Software Verification and Testing - Teardown Sprint
Compliant with MCP specification and CONTRACT.md Section 7.
"""

import sys
import os
import json
from typing import Dict, Any, List, Optional

# Proje kök dizinini sys.path'e ekle (herhangi bir yerden çalıştırılabilsin)
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.engine import run_power_analysis, EngineError
from src.cli import format_success_json, format_error_json, MODE_ALLOWED_PARAMS

TOOL_DEFINITION = {
    "name": "power_analysis",
    "description": "Performs statistical power and sample size calculations according to G*Power specification.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "test": {
                "type": "string",
                "description": "Test family ID (e.g., 't2-indep')",
                "enum": ["t2-indep"]
            },
            "mode": {
                "type": "string",
                "description": "Analysis mode",
                "enum": ["a-priori", "post-hoc", "compromise", "criterion", "sensitivity"]
            },
            "tails": {
                "type": "integer",
                "description": "1 for one-tailed, 2 for two-tailed test",
                "enum": [1, 2]
            },
            "d": {
                "type": "number",
                "description": "Cohen's effect size d (d > 0)"
            },
            "alpha": {
                "type": "number",
                "description": "Type I error probability alpha (0 < alpha < 1)"
            },
            "power": {
                "type": "number",
                "description": "Target or achieved statistical power (1 - beta err prob)"
            },
            "ratio": {
                "type": "number",
                "description": "Allocation ratio N2/N1 (ratio > 0, default 1.0)"
            },
            "n1": {
                "type": "integer",
                "description": "Sample size for group 1 (n1 >= 2)"
            },
            "n2": {
                "type": "integer",
                "description": "Sample size for group 2 (n2 >= 2)"
            },
            "beta_alpha_ratio": {
                "type": "number",
                "description": "Ratio of beta / alpha error probabilities (compromise mode)"
            }
        },
        "required": ["test", "mode"]
    }
}


def execute_power_analysis_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the power_analysis tool using the shared engine.
    Ensures zero logic duplication and exact CLI parity.
    """
    test = arguments.get("test")
    mode = arguments.get("mode")

    if not test:
        return {
            "isError": True,
            "content": [{"type": "text", "text": format_error_json("Parameter 'test' is required", code="MISSING_PARAM", field="test")}]
        }
    if test != "t2-indep":
        return {
            "isError": True,
            "content": [{"type": "text", "text": format_error_json(f"Unsupported test family: '{test}'", code="UNSUPPORTED", field="test")}]
        }
    if not mode:
        return {
            "isError": True,
            "content": [{"type": "text", "text": format_error_json("Parameter 'mode' is required", code="MISSING_PARAM", field="mode")}]
        }
    if mode not in MODE_ALLOWED_PARAMS:
        return {
            "isError": True,
            "content": [{"type": "text", "text": format_error_json(f"Unsupported mode: '{mode}'", code="UNSUPPORTED", field="mode")}]
        }

    # Verify no disallowed params
    allowed = MODE_ALLOWED_PARAMS[mode]
    for key in arguments:
        if key not in allowed:
            return {
                "isError": True,
                "content": [{"type": "text", "text": format_error_json(f"Parameter '{key}' not allowed for mode '{mode}'", code="UNKNOWN_PARAM", field=key)}]
            }

    try:
        result = run_power_analysis(arguments)
        json_output = format_success_json(result)
        return {
            "isError": False,
            "content": [{"type": "text", "text": json_output}]
        }
    except EngineError as e:
        return {
            "isError": True,
            "content": [{"type": "text", "text": format_error_json(e.message, e.code, e.field)}]
        }
    except Exception as e:
        return {
            "isError": True,
            "content": [{"type": "text", "text": format_error_json(f"Internal calculation error: {str(e)}", code="NO_SOLUTION")}]
        }


def handle_json_rpc(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handles an incoming JSON-RPC 2.0 request."""
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    # If it's a notification (no id, like notifications/initialized), do NOT send any response
    if req_id is None:
        return None

    if method == "initialize":
        client_version = params.get("protocolVersion", "2024-11-05")
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": client_version,
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "gpower-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [TOOL_DEFINITION]
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        if tool_name != "power_analysis":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method/Tool '{tool_name}' not found"
                }
            }
        tool_res = execute_power_analysis_tool(arguments)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": tool_res
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Unknown JSON-RPC method: {method}"
            }
        }


def run_stdio_server():
    """Runs standard stdio loop for MCP server."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_json_rpc(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            sys.stdout.write(json.dumps(err_resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_server()
