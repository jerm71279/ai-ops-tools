import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Engineering API Server
Exposes endpoints for engineering tracking and reporting
"""
import os
import subprocess
import threading
from flask import Flask, jsonify, request
from datetime import datetime
from flask_socketio import SocketIO, emit
from flask_cors import CORS # Import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading') # Initialize SocketIO

# Track running jobs
jobs = {}

def run_tool(job_id, script_name, args=None):
    """Run a tool script in background"""
    jobs[job_id]['status'] = 'running'
    jobs[job_id]['started_at'] = datetime.utcnow().isoformat()

    try:
        cmd = ['python', script_name]
        if args:
            cmd.extend(args)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800  # 30 min max
        )

        jobs[job_id]['status'] = 'completed' if result.returncode == 0 else 'failed'
        jobs[job_id]['output'] = result.stdout[-5000:]
        jobs[job_id]['error'] = result.stderr[-2000:] if result.stderr else None
        jobs[job_id]['exit_code'] = result.returncode

    except subprocess.TimeoutExpired:
        jobs[job_id]['status'] = 'timeout'
        jobs[job_id]['error'] = 'Job exceeded 30 minute timeout'
    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)

    jobs[job_id]['completed_at'] = datetime.utcnow().isoformat()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'engineering-api'})

@app.route('/tools', methods=['GET'])
def list_tools():
    return jsonify({
        'tools': [
            {'name': 'engineering_tracker', 'description': 'Engineering projects/tickets API'},
            {'name': 'daily_summary', 'description': 'Generate daily email summary'},
            {'name': 'contract_tracker', 'description': 'Customer contract management'},
            {'name': 'ee_team_dashboard', 'description': 'EE Team dashboard backend'}
        ]
    })

@app.route('/run/<tool_name>', methods=['POST'])
def run_tool_endpoint(tool_name):
    """Trigger a tool to run"""
    valid_tools = {
        'engineering_tracker': 'engineering_tracker.py',
        'daily_summary': 'daily_engineering_summary.py',
        'contract_tracker': 'contract_tracker.py',
        'ee_team_dashboard': 'ee_team_dashboard.py',
        'ecs_dashboard': 'ecs_dashboard.py'
    }

    if tool_name not in valid_tools:
        return jsonify({'error': f'Unknown tool: {tool_name}'}), 404

    args = request.json.get('args', []) if request.is_json else []

    job_id = f"{tool_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    jobs[job_id] = {
        'id': job_id,
        'tool': tool_name,
        'status': 'queued',
        'created_at': datetime.utcnow().isoformat()
    }

    thread = threading.Thread(
        target=run_tool,
        args=(job_id, valid_tools[tool_name], args)
    )
    thread.start()

    return jsonify({'job_id': job_id, 'status': 'queued'}), 202

@app.route('/summary/send', methods=['POST'])
def send_daily_summary():
    """Trigger daily summary email"""
    job_id = f"daily_summary_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    jobs[job_id] = {
        'id': job_id,
        'tool': 'daily_summary',
        'status': 'queued',
        'created_at': datetime.utcnow().isoformat()
    }

    thread = threading.Thread(
        target=run_tool,
        args=(job_id, 'daily_engineering_summary.py', ['--send'])
    )
    thread.start()

    return jsonify({'job_id': job_id, 'status': 'queued', 'message': 'Daily summary email queued'}), 202

@app.route('/jobs', methods=['GET'])
def list_jobs():
    return jsonify({'jobs': list(jobs.values())})

@app.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(jobs[job_id])

@app.route('/broadcast_update', methods=['POST'])
def broadcast_update():
    """
    Receives an update from a client and broadcasts it to all connected WebSocket clients.
    Expected JSON: {"event_type": "data_updated", "data": {"type": "projects", "id": "123"}}
    """
    data = request.json
    if not data or 'event_type' not in data:
        return jsonify({'error': 'Invalid request body'}), 400

    event_type = data['event_type']
    event_data = data.get('data', {})

    print(f"Broadcasting event: {event_type} with data: {event_data}")
    socketio.emit(event_type, event_data)

    return jsonify({'status': 'success', 'message': 'Update broadcasted'}), 200

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True, allow_unsafe_werkzeug=True)
