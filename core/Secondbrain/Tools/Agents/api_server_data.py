import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Data Processing API Server
Exposes endpoints to trigger data import tools
"""
import os
import subprocess
import threading
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

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
            timeout=3600  # 1 hour max
        )

        jobs[job_id]['status'] = 'completed' if result.returncode == 0 else 'failed'
        jobs[job_id]['output'] = result.stdout[-5000:]  # Last 5000 chars
        jobs[job_id]['error'] = result.stderr[-2000:] if result.stderr else None
        jobs[job_id]['exit_code'] = result.returncode

    except subprocess.TimeoutExpired:
        jobs[job_id]['status'] = 'timeout'
        jobs[job_id]['error'] = 'Job exceeded 1 hour timeout'
    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)

    jobs[job_id]['completed_at'] = datetime.utcnow().isoformat()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'data-processing'})

@app.route('/tools', methods=['GET'])
def list_tools():
    return jsonify({
        'tools': [
            {'name': 'sharepoint_importer', 'description': 'Import documents from SharePoint'},
            {'name': 'slack_importer', 'description': 'Import Slack channel exports'},
            {'name': 'slab_importer', 'description': 'Import documentation from Slab'},
            {'name': 'sync_sharepoint', 'description': 'Sync SharePoint sites'},
            {'name': 'download_sharepoint', 'description': 'Download files from SharePoint'}
        ]
    })

@app.route('/run/<tool_name>', methods=['POST'])
def run_tool_endpoint(tool_name):
    """Trigger a tool to run"""
    valid_tools = {
        'sharepoint_importer': 'sharepoint_importer.py',
        'slack_importer': 'slack_importer.py',
        'slab_importer': 'slab_importer.py',
        'sync_sharepoint': 'sync_sharepoint.py',
        'download_sharepoint': 'download_sharepoint.py',
        'download_all_sharepoint': 'download_all_sharepoint.py'
    }

    if tool_name not in valid_tools:
        return jsonify({'error': f'Unknown tool: {tool_name}'}), 404

    # Get optional args from request body
    args = request.json.get('args', []) if request.is_json else []

    # Create job
    job_id = f"{tool_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    jobs[job_id] = {
        'id': job_id,
        'tool': tool_name,
        'status': 'queued',
        'created_at': datetime.utcnow().isoformat()
    }

    # Run in background thread
    thread = threading.Thread(
        target=run_tool,
        args=(job_id, valid_tools[tool_name], args)
    )
    thread.start()

    return jsonify({'job_id': job_id, 'status': 'queued'}), 202

@app.route('/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    return jsonify({'jobs': list(jobs.values())})

@app.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get job status"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(jobs[job_id])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
