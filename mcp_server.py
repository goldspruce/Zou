#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for 'The Quick Initial Doublet' Paper.
Implements the Paper2Agent architecture (Miao, Zou et al., Nature 2026).
Provides standardized JSON-RPC 2.0 stdio tools and resources for AI clients
(Claude Desktop, Cursor, Antigravity, etc.).
"""

import sys
import json
import traceback
from typing import Dict, Any, List

from qid_paper2agent.electrophysiology import ElectrophysiologyEngine
from qid_paper2agent.kinematics import KinematicsEngine
from qid_paper2agent.aging import AgingModel
from qid_paper2agent.knowledge_base import (
    PAPER_METADATA,
    NEURAL_SUBSYSTEMS,
    MOTOR_CONTROL_HIERARCHY,
    search_knowledge_base
)

# Instantiate engines
e_engine = ElectrophysiologyEngine()
k_engine = KinematicsEngine()
a_model = AgingModel(k_engine)

MCP_TOOLS = [
    {
        "name": "simulate_vertical_jump",
        "description": (
            "Simulates ballistic vertical jump kinematics driven by Lower Motor Neuron (LMN) "
            "Quick Initial Doublet (QID). Computes initial Jerk (Hill Ca2+ cooperativity), "
            "peak sustained acceleration, takeoff time, exit velocity, and net jump height clearance."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "frequency_hz": {
                    "type": "number",
                    "description": "Doublet firing frequency in Hz (e.g. 100 for youth baseline, 90 for age 55, 80 for age 70, 75, 50, 25)."
                },
                "custom_jerk": {
                    "type": "number",
                    "description": "Optional explicit Jerk in m/s^3. If omitted, calculated via non-linear Hill equation."
                }
            },
            "required": ["frequency_hz"]
        }
    },
    {
        "name": "calculate_epsp_summation",
        "description": (
            "Calculates synaptic temporal summation, retention fraction (r), Summation Multiplier (M), "
            "Summation Gain (G), and subthreshold depolarization (Vm) of Lower Motor Neurons primed by Upper Motor Neuron (UMN) QIDs."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "frequency_hz": {
                    "type": "number",
                    "description": "UMN firing frequency in Hz (e.g. 200 for healthy M1 baseline, 150 for 25% drop, 100 for 50% drop, 50 for tonic)."
                },
                "tau_ms": {
                    "type": "number",
                    "description": "Optional AMPA EPSP decay time constant in ms (default: 4.0 ms)."
                }
            },
            "required": ["frequency_hz"]
        }
    },
    {
        "name": "predict_aging_trajectory",
        "description": (
            "Predicts LMN QID frequency underclocking, jump clearance loss, dynapenia onset, and "
            "frailty risk across lifespan based on Klass et al. (2008) and Masters Track World Record benchmarks."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "age_years": {
                    "type": "integer",
                    "description": "Chronological age in years (e.g. 25, 55, 70, 80)."
                },
                "is_active_athlete": {
                    "type": "boolean",
                    "description": "True for masters athlete profile (slower rate decline), False for sedentary general population."
                }
            },
            "required": ["age_years"]
        }
    },
    {
        "name": "get_spike_train_schedule",
        "description": (
            "Generates the full millisecond-by-millisecond spike event schedule (Spike 1, Spike 2 (D), Spike 3, ..., EXIT) "
            "with instantaneous Jerk, Acceleration, Velocity, and Position."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "frequency_hz": {
                    "type": "number",
                    "description": "QID frequency in Hz (e.g. 100, 90, 80, 75, 50)."
                }
            },
            "required": ["frequency_hz"]
        }
    },
    {
        "name": "query_paper_knowledge",
        "description": (
            "Queries theoretical claims, physiological mechanisms, citations, and appendix classifications "
            "across the paper's 4 neural subsystems (LMN muscles, UMN engine-start, Cochlear octopus cells, PV+ gamma interneurons)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Question or topic (e.g. 'octopus cells', 'PV+ interneurons', 'phase transition', 'dynapenia', 'McCormick')."
                }
            },
            "required": ["query"]
        }
    }
]

MCP_RESOURCES = [
    {
        "uri": "paper://manuscript_summary",
        "name": "Manuscript Summary & Metadata",
        "mimeType": "application/json"
    },
    {
        "uri": "paper://subsystems",
        "name": "Four Neural Subsystems Reference",
        "mimeType": "application/json"
    },
    {
        "uri": "paper://kinematic_benchmarks",
        "name": "Ground Truth Benchmark Kinematic Tables",
        "mimeType": "application/json"
    }
]


def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    if tool_name == "simulate_vertical_jump":
        freq = float(arguments.get("frequency_hz", 100.0))
        custom_jerk = arguments.get("custom_jerk")
        if custom_jerk is not None:
            custom_jerk = float(custom_jerk)
        res = k_engine.simulate_jump(freq, custom_jerk)
        return json.dumps(res.to_dict(), indent=2)

    elif tool_name == "calculate_epsp_summation":
        freq = float(arguments.get("frequency_hz", 200.0))
        tau = arguments.get("tau_ms")
        if tau is not None:
            custom_engine = ElectrophysiologyEngine(tau_ms=float(tau))
            res = custom_engine.calculate_summation(freq)
        else:
            res = e_engine.calculate_summation(freq)
        return json.dumps(res.to_dict(), indent=2)

    elif tool_name == "predict_aging_trajectory":
        age = int(arguments.get("age_years", 55))
        is_athlete = bool(arguments.get("is_active_athlete", True))
        profile = a_model.evaluate_profile(age, is_athlete)
        return json.dumps(profile.to_dict(), indent=2)

    elif tool_name == "get_spike_train_schedule":
        freq = float(arguments.get("frequency_hz", 100.0))
        res = k_engine.simulate_jump(freq)
        return json.dumps({
            "frequency_hz": freq,
            "takeoff_time_ms": res.takeoff_time_ms,
            "exit_velocity_m_s": res.exit_velocity_m_s,
            "jump_height_m": res.jump_height_m,
            "spikes": [s.to_dict() for s in res.spikes]
        }, indent=2)

    elif tool_name == "query_paper_knowledge":
        q = arguments.get("query", "")
        return json.dumps(search_knowledge_base(q), indent=2)

    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def handle_resource_read(uri: str) -> Dict[str, Any]:
    if uri == "paper://manuscript_summary":
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(PAPER_METADATA, indent=2)
        }
    elif uri == "paper://subsystems":
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(NEURAL_SUBSYSTEMS, indent=2)
        }
    elif uri == "paper://kinematic_benchmarks":
        benchmarks = {
            "100Hz_Baseline": k_engine.simulate_jump(100.0).to_dict(),
            "90Hz_Moderate": k_engine.simulate_jump(90.0).to_dict(),
            "80Hz_Intermediate": k_engine.simulate_jump(80.0).to_dict(),
            "75Hz_NonLinear": k_engine.simulate_jump(75.0).to_dict(),
            "50Hz_SystemicCrash": k_engine.simulate_jump(50.0).to_dict(),
            "25Hz_Singlets": k_engine.simulate_jump(25.0).to_dict()
        }
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(benchmarks, indent=2)
        }
    else:
        raise ValueError(f"Unknown resource: {uri}")


def main():
    """Main JSON-RPC stdio event loop."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                            "resources": {}
                        },
                        "serverInfo": {
                            "name": "qid-paper2agent",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == "notifications/initialized":
                continue
            elif method == "ping":
                res = {"jsonrpc": "2.0", "id": req_id, "result": {}}
            elif method == "tools/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": MCP_TOOLS}
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                content_text = handle_tool_call(tool_name, arguments)
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": content_text
                            }
                        ]
                    }
                }
            elif method == "resources/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"resources": MCP_RESOURCES}
                }
            elif method == "resources/read":
                uri = params.get("uri")
                resource_obj = handle_resource_read(uri)
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "contents": [resource_obj]
                    }
                }
            else:
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }

            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        except Exception as e:
            err_res = {
                "jsonrpc": "2.0",
                "id": req_id if "req_id" in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e),
                    "data": traceback.format_exc()
                }
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
