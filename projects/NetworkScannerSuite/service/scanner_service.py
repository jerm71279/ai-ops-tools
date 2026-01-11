#!/usr/bin/env python3
"""
Obera Network Scanner Service
FastAPI backend for network scanning with web interface
"""

import asyncio
import json
import subprocess
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configuration
SERVICE_DIR = Path(__file__).parent
SCANS_DIR = SERVICE_DIR / "scans"
SCANS_DIR.mkdir(exist_ok=True)

# Store active scans and websocket connections
active_scans = {}
websocket_connections: List[WebSocket] = []


# Pydantic Models
class ScanConfig(BaseModel):
    target: str = Field(..., description="Target network in CIDR notation (e.g., 192.168.1.0/24)")
    scan_type: str = Field(default="standard", description="Scan type: quick, standard, or intense")
    name: Optional[str] = Field(default=None, description="Custom name for this scan")
    exclusions: List[str] = Field(default=[], description="IPs to exclude from scan")


class ScanStatus(BaseModel):
    scan_id: str
    status: str  # pending, running, completed, failed, cancelled
    target: str
    scan_type: str
    started_at: Optional[str]
    completed_at: Optional[str]
    hosts_found: int
    progress: int  # 0-100
    current_phase: str
    output_dir: str


class ScanResult(BaseModel):
    scan_id: str
    hosts: List[dict]
    summary: dict
    files: List[str]


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Obera Network Scanner Service starting...")
    print(f"Scans directory: {SCANS_DIR}")
    yield
    # Shutdown
    print("Shutting down scanner service...")
    # Cancel any active scans
    for scan_id in list(active_scans.keys()):
        if active_scans[scan_id].get("process"):
            active_scans[scan_id]["process"].terminate()


# Create FastAPI app
app = FastAPI(
    title="Obera Network Scanner",
    description="Network scanning service with web interface",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket manager for real-time updates
async def broadcast_update(message: dict):
    """Send update to all connected websocket clients"""
    for connection in websocket_connections:
        try:
            await connection.send_json(message)
        except:
            pass


# Scan execution
async def run_scan(scan_id: str, config: ScanConfig):
    """Execute network scan in background"""
    scan_info = active_scans[scan_id]
    output_dir = Path(scan_info["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build nmap commands for each phase
    phases = []

    if config.scan_type == "quick":
        phases = [
            ("Host Discovery", f"nmap -sn {config.target} -oA {output_dir}/01_discovery"),
        ]
    elif config.scan_type == "standard":
        phases = [
            ("Host Discovery", f"nmap -sn {config.target} -oA {output_dir}/01_discovery"),
            ("Port Scan", f"nmap -F {config.target} -oA {output_dir}/02_ports"),
            ("Service Detection", f"nmap -sV {config.target} -oA {output_dir}/03_services"),
        ]
    else:  # intense
        phases = [
            ("Host Discovery", f"nmap -sn {config.target} -oA {output_dir}/01_discovery"),
            ("Port Scan", f"nmap -p- -T4 {config.target} -oA {output_dir}/02_ports"),
            ("Service Detection", f"nmap -sV -sC {config.target} -oA {output_dir}/03_services"),
            ("OS Detection", f"nmap -O {config.target} -oA {output_dir}/04_os"),
        ]

    total_phases = len(phases)
    hosts_found = 0

    try:
        for i, (phase_name, cmd) in enumerate(phases):
            # Update status
            scan_info["current_phase"] = phase_name
            scan_info["progress"] = int((i / total_phases) * 100)

            await broadcast_update({
                "type": "scan_progress",
                "scan_id": scan_id,
                "phase": phase_name,
                "progress": scan_info["progress"],
                "message": f"Running {phase_name}..."
            })

            # Run nmap command
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            scan_info["process"] = process

            stdout, stderr = await process.communicate()
            output = stdout.decode()

            # Send output to websockets
            await broadcast_update({
                "type": "scan_output",
                "scan_id": scan_id,
                "phase": phase_name,
                "output": output
            })

            # Count hosts from discovery phase
            if "discovery" in cmd:
                hosts_found = output.count("Host is up")
                scan_info["hosts_found"] = hosts_found

            # Check if cancelled
            if scan_info.get("cancelled"):
                scan_info["status"] = "cancelled"
                await broadcast_update({
                    "type": "scan_cancelled",
                    "scan_id": scan_id
                })
                return

        # Scan completed
        scan_info["status"] = "completed"
        scan_info["completed_at"] = datetime.now().isoformat()
        scan_info["progress"] = 100
        scan_info["current_phase"] = "Complete"

        # Parse results
        results = parse_scan_results(output_dir)

        # Save summary
        summary_file = output_dir / "SUMMARY.json"
        with open(summary_file, "w") as f:
            json.dump({
                "scan_id": scan_id,
                "target": config.target,
                "scan_type": config.scan_type,
                "hosts_found": hosts_found,
                "started_at": scan_info["started_at"],
                "completed_at": scan_info["completed_at"],
                "results": results
            }, f, indent=2)

        await broadcast_update({
            "type": "scan_completed",
            "scan_id": scan_id,
            "hosts_found": hosts_found,
            "results": results
        })

    except Exception as e:
        scan_info["status"] = "failed"
        scan_info["error"] = str(e)
        await broadcast_update({
            "type": "scan_failed",
            "scan_id": scan_id,
            "error": str(e)
        })


def parse_scan_results(output_dir: Path) -> dict:
    """Parse nmap output files into structured results"""
    results = {
        "hosts": [],
        "services": [],
        "os_matches": []
    }

    # Parse gnmap files for quick host extraction
    for gnmap_file in output_dir.glob("*.gnmap"):
        with open(gnmap_file) as f:
            for line in f:
                if "Status: Up" in line:
                    ip_match = re.search(r'Host: (\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        ip = ip_match.group(1)
                        if ip not in [h["ip"] for h in results["hosts"]]:
                            results["hosts"].append({"ip": ip, "ports": [], "os": None})

                # Parse ports
                if "Ports:" in line:
                    ip_match = re.search(r'Host: (\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        ip = ip_match.group(1)
                        ports_section = line.split("Ports:")[1]
                        port_matches = re.findall(r'(\d+)/open/tcp//([^/]*)', ports_section)
                        for port, service in port_matches:
                            for host in results["hosts"]:
                                if host["ip"] == ip:
                                    host["ports"].append({
                                        "port": int(port),
                                        "protocol": "tcp",
                                        "service": service.strip()
                                    })

    return results


# API Routes
@app.get("/")
async def root():
    """Serve web interface"""
    index_path = SERVICE_DIR.parent / "web-ui" / "public" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Obera Network Scanner API", "version": "1.0.0", "docs": "/docs"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    # Check if nmap is available
    try:
        result = subprocess.run(["nmap", "--version"], capture_output=True, text=True)
        nmap_available = result.returncode == 0
        nmap_version = result.stdout.split('\n')[0] if nmap_available else None
    except:
        nmap_available = False
        nmap_version = None

    return {
        "status": "healthy",
        "nmap_available": nmap_available,
        "nmap_version": nmap_version,
        "scans_dir": str(SCANS_DIR),
        "active_scans": len([s for s in active_scans.values() if s["status"] == "running"])
    }


@app.post("/api/scans", response_model=ScanStatus)
async def start_scan(config: ScanConfig, background_tasks: BackgroundTasks):
    """Start a new network scan"""
    # Generate scan ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scan_name = config.name or config.target.replace("/", "_").replace(".", "-")
    scan_id = f"{scan_name}_{timestamp}"

    # Create output directory
    output_dir = SCANS_DIR / scan_id

    # Initialize scan info
    scan_info = {
        "scan_id": scan_id,
        "status": "running",
        "target": config.target,
        "scan_type": config.scan_type,
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "hosts_found": 0,
        "progress": 0,
        "current_phase": "Initializing",
        "output_dir": str(output_dir),
        "process": None,
        "cancelled": False
    }
    active_scans[scan_id] = scan_info

    # Start scan in background
    background_tasks.add_task(run_scan, scan_id, config)

    return ScanStatus(**{k: v for k, v in scan_info.items() if k != "process"})


@app.get("/api/scans", response_model=List[ScanStatus])
async def list_scans():
    """List all scans (active and completed)"""
    scans = []

    # Active scans
    for scan_id, info in active_scans.items():
        scans.append(ScanStatus(**{k: v for k, v in info.items() if k not in ["process", "cancelled"]}))

    # Completed scans from disk
    for scan_dir in SCANS_DIR.iterdir():
        if scan_dir.is_dir() and scan_dir.name not in active_scans:
            summary_file = scan_dir / "SUMMARY.json"
            if summary_file.exists():
                with open(summary_file) as f:
                    summary = json.load(f)
                    scans.append(ScanStatus(
                        scan_id=summary.get("scan_id", scan_dir.name),
                        status="completed",
                        target=summary.get("target", "unknown"),
                        scan_type=summary.get("scan_type", "unknown"),
                        started_at=summary.get("started_at"),
                        completed_at=summary.get("completed_at"),
                        hosts_found=summary.get("hosts_found", 0),
                        progress=100,
                        current_phase="Complete",
                        output_dir=str(scan_dir)
                    ))

    return sorted(scans, key=lambda x: x.started_at or "", reverse=True)


@app.get("/api/scans/{scan_id}")
async def get_scan(scan_id: str):
    """Get scan details and results"""
    # Check active scans
    if scan_id in active_scans:
        info = active_scans[scan_id]
        return {
            "status": ScanStatus(**{k: v for k, v in info.items() if k not in ["process", "cancelled"]}),
            "results": None if info["status"] == "running" else parse_scan_results(Path(info["output_dir"]))
        }

    # Check completed scans
    scan_dir = SCANS_DIR / scan_id
    if scan_dir.exists():
        summary_file = scan_dir / "SUMMARY.json"
        if summary_file.exists():
            with open(summary_file) as f:
                return json.load(f)

    raise HTTPException(status_code=404, detail="Scan not found")


@app.delete("/api/scans/{scan_id}")
async def cancel_scan(scan_id: str):
    """Cancel a running scan"""
    if scan_id not in active_scans:
        raise HTTPException(status_code=404, detail="Scan not found")

    scan_info = active_scans[scan_id]
    if scan_info["status"] != "running":
        raise HTTPException(status_code=400, detail="Scan is not running")

    # Cancel the scan
    scan_info["cancelled"] = True
    if scan_info.get("process"):
        scan_info["process"].terminate()

    return {"message": "Scan cancelled", "scan_id": scan_id}


@app.get("/api/scans/{scan_id}/files")
async def list_scan_files(scan_id: str):
    """List output files for a scan"""
    scan_dir = SCANS_DIR / scan_id
    if not scan_dir.exists():
        raise HTTPException(status_code=404, detail="Scan not found")

    files = []
    for f in scan_dir.iterdir():
        files.append({
            "name": f.name,
            "size": f.stat().st_size,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        })

    return files


@app.get("/api/scans/{scan_id}/files/{filename}")
async def download_scan_file(scan_id: str, filename: str):
    """Download a specific scan output file"""
    file_path = SCANS_DIR / scan_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, filename=filename)


# WebSocket for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time scan updates"""
    await websocket.accept()
    websocket_connections.append(websocket)

    try:
        # Send current status of all active scans
        for scan_id, info in active_scans.items():
            if info["status"] == "running":
                await websocket.send_json({
                    "type": "scan_status",
                    "scan_id": scan_id,
                    "status": info["status"],
                    "progress": info["progress"],
                    "phase": info["current_phase"]
                })

        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Handle any client messages if needed

    except WebSocketDisconnect:
        websocket_connections.remove(websocket)


# Main entry point
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("OBERA NETWORK SCANNER SERVICE")
    print("=" * 60)
    print(f"Starting server on http://0.0.0.0:8080")
    print(f"API docs available at http://localhost:8080/docs")
    print("=" * 60)

    uvicorn.run(
        "scanner_service:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
