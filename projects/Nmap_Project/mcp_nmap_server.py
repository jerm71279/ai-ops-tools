#!/usr/bin/env python3
"""
MCP Server for Nmap Network Discovery
Allows Claude to run nmap commands remotely on customer networks
"""

import asyncio
import json
import subprocess
import os
from datetime import datetime
from pathlib import Path
from typing import Any

# MCP SDK imports
try:
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
except ImportError:
    print("Error: MCP SDK not installed. Install with: pip install mcp")
    exit(1)

# Initialize MCP server
server = Server("nmap-network-discovery")

# Configuration
SCRIPT_DIR = Path(__file__).parent
SCANS_DIR = SCRIPT_DIR / "scans"
SCANS_DIR.mkdir(exist_ok=True)

# Store scan history
scan_history = []


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available nmap tools"""
    return [
        types.Tool(
            name="nmap_ping_sweep",
            description="Discover live hosts on a network using ping sweep. Fast host discovery without port scanning.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target network in CIDR notation (e.g., 192.168.1.0/24)"
                    },
                    "exclude": {
                        "type": "string",
                        "description": "Optional: Comma-separated list of IPs to exclude"
                    }
                },
                "required": ["target"]
            }
        ),
        types.Tool(
            name="nmap_port_scan",
            description="Scan ports on target hosts. Can scan specific ports or common ports.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target IP or network (e.g., 192.168.1.10 or 192.168.1.0/24)"
                    },
                    "ports": {
                        "type": "string",
                        "description": "Port specification (e.g., '80,443' or '1-1000' or 'top-100'). Leave empty for fast scan (top 1000 ports)"
                    },
                    "scan_type": {
                        "type": "string",
                        "enum": ["fast", "full", "udp"],
                        "description": "Scan type: fast (top 1000), full (all TCP), or udp"
                    }
                },
                "required": ["target"]
            }
        ),
        types.Tool(
            name="nmap_service_detection",
            description="Detect services and versions running on open ports. Essential for infrastructure planning.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target IP or network"
                    },
                    "ports": {
                        "type": "string",
                        "description": "Optional: Specific ports to check (e.g., '22,80,443')"
                    }
                },
                "required": ["target"]
            }
        ),
        types.Tool(
            name="nmap_os_detection",
            description="Detect operating systems on target hosts. Useful for compatibility planning.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target IP or network"
                    }
                },
                "required": ["target"]
            }
        ),
        types.Tool(
            name="nmap_comprehensive_scan",
            description="Comprehensive scan combining service detection, OS detection, and common scripts. Best for detailed infrastructure analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target IP or network"
                    },
                    "aggressive": {
                        "type": "boolean",
                        "description": "Use aggressive scanning (faster but more detectable)"
                    }
                },
                "required": ["target"]
            }
        ),
        types.Tool(
            name="nmap_intense_scan",
            description="Zenmap-style intense scan: nmap -T4 -A -v. Enables OS detection, version detection, script scanning, and traceroute with verbose output.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target network in CIDR notation (e.g., 192.168.1.0/24) or single IP"
                    },
                    "exclude": {
                        "type": "string",
                        "description": "Optional: Comma-separated list of IPs to exclude"
                    }
                },
                "required": ["target"]
            }
        ),
        types.Tool(
            name="nmap_custom_command",
            description="Run a custom nmap command with full control. For advanced users.",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Full nmap command arguments (without 'nmap' prefix)"
                    }
                },
                "required": ["command"]
            }
        ),
        types.Tool(
            name="get_scan_results",
            description="Retrieve results from a previous scan by scan ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "scan_id": {
                        "type": "string",
                        "description": "Scan ID returned from previous scan"
                    }
                },
                "required": ["scan_id"]
            }
        ),
        types.Tool(
            name="list_scan_history",
            description="List all previous scans with their IDs and basic information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


def run_nmap_command(args: list[str], scan_name: str) -> dict[str, Any]:
    """Execute nmap command and save results"""
    
    # Generate scan ID and output paths
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scan_id = f"{scan_name}_{timestamp}"
    output_base = SCANS_DIR / scan_id
    
    # Build nmap command with output options
    cmd = ["nmap"] + args + [
        "-oN", f"{output_base}.nmap",
        "-oX", f"{output_base}.xml",
        "-oG", f"{output_base}.gnmap"
    ]
    
    try:
        # Run nmap
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        # Read the normal output file
        output_file = f"{output_base}.nmap"
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                output = f.read()
        else:
            output = result.stdout
        
        # Store in history
        scan_record = {
            "scan_id": scan_id,
            "scan_name": scan_name,
            "timestamp": timestamp,
            "command": " ".join(cmd),
            "target": args[-1] if args else "unknown",
            "output_files": {
                "nmap": f"{output_base}.nmap",
                "xml": f"{output_base}.xml",
                "gnmap": f"{output_base}.gnmap"
            }
        }
        scan_history.append(scan_record)
        
        return {
            "success": True,
            "scan_id": scan_id,
            "output": output,
            "stderr": result.stderr if result.stderr else None,
            "return_code": result.returncode,
            "output_files": scan_record["output_files"]
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Scan timed out after 1 hour"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution"""
    
    if arguments is None:
        arguments = {}
    
    try:
        if name == "nmap_ping_sweep":
            target = arguments["target"]
            exclude = arguments.get("exclude", "")
            
            args = ["-sn", "-PE", "-n", target]
            if exclude:
                # Create temporary exclude file
                exclude_file = SCANS_DIR / "temp_exclude.txt"
                with open(exclude_file, 'w') as f:
                    f.write(exclude.replace(",", "\n"))
                args.extend(["--excludefile", str(exclude_file)])
            
            result = run_nmap_command(args, "ping_sweep")
            
        elif name == "nmap_port_scan":
            target = arguments["target"]
            ports = arguments.get("ports", "")
            scan_type = arguments.get("scan_type", "fast")
            
            if scan_type == "fast":
                args = ["-F", target]
            elif scan_type == "full":
                args = ["-p-", target]
            elif scan_type == "udp":
                args = ["-sU", target]
            else:
                args = [target]
            
            if ports:
                args.insert(0, f"-p{ports}")
            
            result = run_nmap_command(args, "port_scan")
            
        elif name == "nmap_service_detection":
            target = arguments["target"]
            ports = arguments.get("ports", "")
            
            args = ["-sV", target]
            if ports:
                args.insert(0, f"-p{ports}")
            
            result = run_nmap_command(args, "service_detection")
            
        elif name == "nmap_os_detection":
            target = arguments["target"]
            args = ["-O", target]
            
            result = run_nmap_command(args, "os_detection")
            
        elif name == "nmap_comprehensive_scan":
            target = arguments["target"]
            aggressive = arguments.get("aggressive", False)
            
            if aggressive:
                args = ["-A", "-T4", target]
            else:
                args = ["-sV", "-O", "-sC", target]
            
            result = run_nmap_command(args, "comprehensive")
            
        elif name == "nmap_intense_scan":
            target = arguments["target"]
            exclude = arguments.get("exclude", "")
            
            # Zenmap intense scan: -T4 -A -v
            args = ["-T4", "-A", "-v", target]
            
            if exclude:
                # Create temporary exclude file
                exclude_file = SCANS_DIR / "temp_exclude.txt"
                with open(exclude_file, 'w') as f:
                    f.write(exclude.replace(",", "\n"))
                args.extend(["--excludefile", str(exclude_file)])
            
            result = run_nmap_command(args, "intense_scan")
            
        elif name == "nmap_custom_command":
            command = arguments["command"]
            args = command.split()
            
            result = run_nmap_command(args, "custom")
            
        elif name == "get_scan_results":
            scan_id = arguments["scan_id"]
            
            # Find scan in history
            scan_record = next((s for s in scan_history if s["scan_id"] == scan_id), None)
            
            if not scan_record:
                result = {
                    "success": False,
                    "error": f"Scan ID {scan_id} not found"
                }
            else:
                # Read the output file
                output_file = scan_record["output_files"]["nmap"]
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        output = f.read()
                    result = {
                        "success": True,
                        "scan_id": scan_id,
                        "output": output,
                        "scan_info": scan_record
                    }
                else:
                    result = {
                        "success": False,
                        "error": "Output file not found"
                    }
        
        elif name == "list_scan_history":
            result = {
                "success": True,
                "total_scans": len(scan_history),
                "scans": [
                    {
                        "scan_id": s["scan_id"],
                        "scan_name": s["scan_name"],
                        "timestamp": s["timestamp"],
                        "target": s["target"]
                    }
                    for s in scan_history
                ]
            }
        
        else:
            result = {
                "success": False,
                "error": f"Unknown tool: {name}"
            }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
        )]


async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="nmap-network-discovery",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
